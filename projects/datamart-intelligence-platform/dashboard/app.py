"""DataMart BI Dashboard & Builder — learn dashboarding by doing.

Two things in one surface:
  1. Live KPIs over the real warehouse (what a dashboard looks like).
  2. A BUILDER — students write a read-only SQL query, pick a chart type and
     axes, preview it, and add it to a dashboard that persists for the session.
     This is the hands-on counterpart to the Unified Dashboards sprint: you don't
     just compute the metrics, you build the dashboard that shows them.

Runs as the compose `dashboard` service (host :8083), linked from the learning
app's Platform page. All SQL runs in a READ-ONLY transaction — safe to explore.
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

st.set_page_config(page_title="DataMart BI Builder", page_icon="📊", layout="wide")

_CONN = dict(
    host=os.environ.get("PGHOST", "postgres"),
    port=int(os.environ.get("PGPORT", "5432")),
    user=os.environ.get("PGUSER", "airflow"),
    password=os.environ.get("PGPASSWORD", "airflow"),
    dbname=os.environ.get("PGDATABASE", "datamart"),
)

_EXAMPLES = {
    "Revenue by category":
        "SELECT category, SUM(total_amount) AS revenue\n"
        "FROM raw.orders GROUP BY category ORDER BY revenue DESC",
    "Revenue by day":
        "SELECT order_date::date AS day, SUM(total_amount) AS revenue\n"
        "FROM raw.orders GROUP BY day ORDER BY day",
    "Top customers":
        "SELECT c.customer_name, SUM(o.total_amount) AS spend\n"
        "FROM raw.orders o JOIN raw.customers c ON o.customer_id = c.customer_id\n"
        "GROUP BY c.customer_name ORDER BY spend DESC LIMIT 10",
    "Orders per status":
        "SELECT status, COUNT(*) AS orders\n"
        "FROM raw.orders GROUP BY status ORDER BY orders DESC",
}


def run_readonly(sql: str) -> pd.DataFrame:
    """Run a query in a READ-ONLY transaction — writes raise, so exploring is safe."""
    conn = psycopg2.connect(**_CONN)
    try:
        conn.set_session(readonly=True, autocommit=True)
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def make_chart(df: pd.DataFrame, kind: str, x: str, y: str):
    if kind == "Bar":
        return px.bar(df, x=x, y=y, color_discrete_sequence=px.colors.sequential.Blugrn)
    if kind == "Line":
        return px.line(df, x=x, y=y, markers=True)
    if kind == "Area":
        return px.area(df, x=x, y=y)
    if kind == "Scatter":
        return px.scatter(df, x=x, y=y)
    if kind == "Pie":
        return px.pie(df, names=x, values=y)
    return None


st.title("📊 DataMart Intelligence — build a dashboard")
st.caption("Live warehouse data. Write a read-only query, chart it, and add it to "
           "your dashboard — the hands-on side of the **Unified Dashboards** sprint.")

# ---- live KPIs -----------------------------------------------------------
try:
    k = run_readonly("""
        SELECT COUNT(*)::int AS orders, COUNT(DISTINCT customer_id)::int AS customers,
               COALESCE(SUM(total_amount),0)::float AS revenue,
               COALESCE(AVG(total_amount),0)::float AS avg_order
        FROM raw.orders
    """).iloc[0]
    a, b, c, d = st.columns(4)
    a.metric("Revenue", f"${k.revenue:,.2f}")
    b.metric("Orders", f"{int(k.orders):,}")
    c.metric("Customers", f"{int(k.customers):,}")
    d.metric("Avg order", f"${k.avg_order:,.2f}")
except Exception as exc:  # noqa: BLE001
    st.warning(f"Can't reach the warehouse yet ({exc.__class__.__name__}). Bring the "
               "stack up with `./platform.sh up`, seed it, then refresh.")
    st.stop()

st.divider()
left, right = st.columns([2, 3], gap="large")

# ---- builder: query + chart config --------------------------------------
if "sql" not in st.session_state:
    st.session_state.sql = _EXAMPLES["Revenue by category"]
if "dashboard" not in st.session_state:
    st.session_state.dashboard = []  # list of {title, sql, kind, x, y}

with left:
    st.subheader("1 · Query")
    st.caption("Start from an example, or write your own (read-only):")
    ex_cols = st.columns(2)
    for i, (name, sql) in enumerate(_EXAMPLES.items()):
        if ex_cols[i % 2].button(name, use_container_width=True, key=f"ex-{name}"):
            st.session_state.sql = sql
            st.rerun()
    st.session_state.sql = st.text_area("SQL", value=st.session_state.sql, height=150,
                                        label_visibility="collapsed")

with right:
    st.subheader("2 · Chart")
    try:
        df = run_readonly(st.session_state.sql)
    except Exception as exc:  # noqa: BLE001 - bad SQL is the learner's, show it kindly
        st.error(f"Query error: {exc}")
        st.stop()
    if df.empty:
        st.info("Query returned no rows.")
        st.stop()
    cols = list(df.columns)
    cfg = st.columns(3)
    kind = cfg[0].selectbox("Type", ["Bar", "Line", "Area", "Scatter", "Pie", "Table"])
    x = cfg[1].selectbox("X / label", cols, index=0)
    y = cfg[2].selectbox("Y / value", cols, index=min(1, len(cols) - 1))
    if kind == "Table":
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.plotly_chart(make_chart(df, kind, x, y), use_container_width=True)
    title = st.text_input("Chart title", value=f"{y} by {x}")
    if st.button("➕ Add to my dashboard", type="primary"):
        st.session_state.dashboard.append(
            {"title": title, "sql": st.session_state.sql, "kind": kind, "x": x, "y": y})
        st.success(f"Added “{title}”.")

# ---- the assembled dashboard --------------------------------------------
st.divider()
head = st.columns([4, 1])
head[0].header(f"My dashboard · {len(st.session_state.dashboard)} chart(s)")
if st.session_state.dashboard and head[1].button("Clear all"):
    st.session_state.dashboard = []
    st.rerun()

if not st.session_state.dashboard:
    st.caption("Build a chart above and click **Add to my dashboard** — your charts "
               "collect here into a dashboard (kept for this session).")
else:
    grid = st.columns(2, gap="large")
    for i, ch in enumerate(list(st.session_state.dashboard)):
        with grid[i % 2].container(border=True):
            top = st.columns([5, 1])
            top[0].markdown(f"**{ch['title']}**")
            if top[1].button("🗑", key=f"rm-{i}", help="Remove"):
                st.session_state.dashboard.pop(i)
                st.rerun()
            try:
                d = run_readonly(ch["sql"])
                if ch["kind"] == "Table":
                    st.dataframe(d, use_container_width=True, hide_index=True)
                else:
                    st.plotly_chart(make_chart(d, ch["kind"], ch["x"], ch["y"]),
                                    use_container_width=True, key=f"ch-{i}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Couldn't render: {exc}")
