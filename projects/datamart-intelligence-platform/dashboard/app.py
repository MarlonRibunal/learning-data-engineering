"""DataMart BI Builder — learn dashboarding by doing.

Two things in one surface:
  1. Live KPIs over the real warehouse (what a dashboard looks like).
  2. A BUILDER — students write a read-only SQL query, pick a chart type and
     axes, preview it, and add it to a dashboard. This is the hands-on
     counterpart to the Unified Dashboards sprint: you don't just compute the
     metrics, you build the dashboard that shows them.

Everything a learner does — their profile, their saved dashboard, and the
exact editor state they left off in — is persisted in the `app` schema of the
warehouse Postgres, which lives on the `postgres_data` named volume. It
survives `docker compose down` and a full power-down: come back, type the same
profile name, and your work is exactly where you left it. All learner SQL runs
in a READ-ONLY transaction, so exploring is always safe; the app writes its own
metadata through a separate connection.

Runs as the compose `dashboard` service (host :8083), linked from the learning
app's Platform page.
"""

from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

# Optional AI tutor — only wired up when an Anthropic key is present.
try:  # pragma: no cover - import guard
    import anthropic
except Exception:  # noqa: BLE001
    anthropic = None

APP_NAME = "DataMart BI Builder"
LEARNING_APP_URL = os.environ.get("LEARNING_APP_URL", "http://localhost:8501")
TUTOR_MODEL = os.environ.get("TUTOR_MODEL", "claude-opus-4-8")

st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide")

_CONN = dict(
    host=os.environ.get("PGHOST", "postgres"),
    port=int(os.environ.get("PGPORT", "5432")),
    user=os.environ.get("PGUSER", "airflow"),
    password=os.environ.get("PGPASSWORD", "airflow"),
    dbname=os.environ.get("PGDATABASE", "datamart"),
)

# One ink-derived sequence used by every chart type, so switching chart type
# never reshuffles the color language and nothing clashes with the platform's
# monochrome palette (config.toml theming + the CSS below).
_INK_SEQ = ["#1d1e21", "#5b6169", "#9aa0a8", "#3a3f46", "#c3c7cd", "#767c84"]
_AXIS = "#6b7280"

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

_CSS = """
<style>
:root {
  --ink:#17181b; --ink-2:#3a3f46; --muted:#6b7280;
  --bg:#f6f7f9; --surface:#ffffff; --border:#e6e8eb; --accent:#1d1e21;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ink:#e7e8ea; --ink-2:#c3c7cd; --muted:#9aa0a8;
    --bg:#0e0f11; --surface:#17181b; --border:#2a2c30; --accent:#e7e8ea;
  }
}
.stApp { background: var(--bg); }
#MainMenu, header [data-testid="stToolbar"], footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }

/* Hero */
.hero-title { font-size: 1.9rem; font-weight: 700; letter-spacing:-.02em;
  color: var(--ink); margin: 0 0 .2rem; }
.hero-sub { color: var(--muted); font-size: .95rem; margin: 0 0 .1rem; }
.pill { display:inline-block; font-size:.72rem; font-weight:600; letter-spacing:.02em;
  color: var(--muted); border:1px solid var(--border); border-radius:999px;
  padding:.12rem .55rem; margin-right:.4rem; background: var(--surface); }
.backlink a { color: var(--muted); text-decoration:none; font-size:.85rem; }
.backlink a:hover { color: var(--ink); }

/* KPI metric cards */
[data-testid="stMetric"] {
  background: var(--surface); border:1px solid var(--border); border-radius:14px;
  padding: 1rem 1.1rem; box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
[data-testid="stMetricLabel"] { color: var(--muted); font-weight:600;
  text-transform:uppercase; letter-spacing:.04em; font-size:.7rem; }
[data-testid="stMetricValue"] { color: var(--ink); font-weight:700;
  letter-spacing:-.02em; }

/* Section headers */
h3, [data-testid="stHeading"] h3 { color: var(--ink); letter-spacing:-.01em; }

/* Buttons: quiet by default, ink when primary */
.stButton > button {
  border-radius:10px; border:1px solid var(--border); background: var(--surface);
  color: var(--ink); font-weight:600; transition: all .12s ease;
}
.stButton > button:hover { border-color: var(--accent); }
.stButton > button[kind="primary"] {
  background: var(--accent); border-color: var(--accent);
  color: var(--bg);
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.15); }

/* Chart cards */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius:14px; border:1px solid var(--border);
}
hr { border-color: var(--border); }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


# ---- database helpers ----------------------------------------------------
def run_readonly(sql: str) -> pd.DataFrame:
    """Run a learner query in a READ-ONLY transaction — writes raise, so it's safe."""
    conn = psycopg2.connect(**_CONN)
    try:
        conn.set_session(readonly=True, autocommit=True)
        return pd.read_sql(sql, conn)
    finally:
        conn.close()


def _admin(sql: str, params: tuple = (), *, fetch: bool = False):
    """Run app-metadata SQL on a writable connection (separate from learner SQL)."""
    conn = psycopg2.connect(**_CONN)
    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None
    finally:
        conn.close()


def ensure_store() -> None:
    """Create the app schema/tables. Idempotent — cheap to call each run."""
    _admin("""
        CREATE SCHEMA IF NOT EXISTS app;
        CREATE TABLE IF NOT EXISTS app.dashboards (
            id BIGSERIAL PRIMARY KEY,
            profile TEXT NOT NULL,
            title TEXT NOT NULL,
            sql TEXT NOT NULL,
            kind TEXT NOT NULL,
            x TEXT, y TEXT,
            position INT NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS dashboards_profile_idx
            ON app.dashboards(profile, position, id);
        CREATE TABLE IF NOT EXISTS app.workspace (
            profile TEXT PRIMARY KEY,
            sql TEXT, kind TEXT, x TEXT, y TEXT, title TEXT,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)


def list_profiles() -> list[str]:
    rows = _admin(
        "SELECT profile, MAX(updated_at) AS t FROM app.workspace GROUP BY profile "
        "UNION ALL SELECT profile, MAX(created_at) FROM app.dashboards GROUP BY profile",
        fetch=True) or []
    seen: dict[str, object] = {}
    for name, t in rows:
        if name not in seen or (t and seen[name] and t > seen[name]):
            seen[name] = t
    return sorted(seen, key=lambda n: seen[n] or "", reverse=True)


def load_dashboard(profile: str) -> list[dict]:
    rows = _admin(
        "SELECT id, title, sql, kind, x, y FROM app.dashboards "
        "WHERE profile=%s ORDER BY position, id", (profile,), fetch=True) or []
    return [dict(id=r[0], title=r[1], sql=r[2], kind=r[3], x=r[4], y=r[5]) for r in rows]


def add_chart(profile: str, chart: dict) -> None:
    _admin(
        "INSERT INTO app.dashboards (profile, title, sql, kind, x, y, position) "
        "VALUES (%s,%s,%s,%s,%s,%s, "
        "COALESCE((SELECT MAX(position)+1 FROM app.dashboards WHERE profile=%s), 0))",
        (profile, chart["title"], chart["sql"], chart["kind"],
         chart["x"], chart["y"], profile))


def remove_chart(chart_id: int) -> None:
    _admin("DELETE FROM app.dashboards WHERE id=%s", (chart_id,))


def clear_dashboard(profile: str) -> None:
    _admin("DELETE FROM app.dashboards WHERE profile=%s", (profile,))


def load_workspace(profile: str) -> dict | None:
    rows = _admin(
        "SELECT sql, kind, x, y, title FROM app.workspace WHERE profile=%s",
        (profile,), fetch=True) or []
    if not rows:
        return None
    sql, kind, x, y, title = rows[0]
    return dict(sql=sql, kind=kind, x=x, y=y, title=title)


def save_workspace(profile: str, sql, kind, x, y, title) -> None:
    _admin("""
        INSERT INTO app.workspace (profile, sql, kind, x, y, title, updated_at)
        VALUES (%s,%s,%s,%s,%s,%s, now())
        ON CONFLICT (profile) DO UPDATE SET
            sql=EXCLUDED.sql, kind=EXCLUDED.kind, x=EXCLUDED.x,
            y=EXCLUDED.y, title=EXCLUDED.title, updated_at=now()
    """, (profile, sql, kind, x, y, title))


def make_chart(df: pd.DataFrame, kind: str, x: str, y: str):
    if kind == "Bar":
        fig = px.bar(df, x=x, y=y, color_discrete_sequence=_INK_SEQ)
    elif kind == "Line":
        fig = px.line(df, x=x, y=y, markers=True, color_discrete_sequence=_INK_SEQ)
    elif kind == "Area":
        fig = px.area(df, x=x, y=y, color_discrete_sequence=_INK_SEQ)
    elif kind == "Scatter":
        fig = px.scatter(df, x=x, y=y, color_discrete_sequence=_INK_SEQ)
    elif kind == "Pie":
        fig = px.pie(df, names=x, values=y, color_discrete_sequence=_INK_SEQ)
    else:
        return None
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=_AXIS, family="sans-serif"),
        margin=dict(l=10, r=10, t=10, b=10), legend_title_text="")
    fig.update_xaxes(gridcolor="rgba(148,163,184,.18)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,.18)", zeroline=False)
    return fig


# ---- header --------------------------------------------------------------
st.markdown(
    f'<div class="backlink"><a href="{LEARNING_APP_URL}">&larr; Back to the '
    'learning platform</a></div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="hero-title">📊 {APP_NAME}</div>'
    '<div class="hero-sub">Live warehouse data. Write a read-only query, chart it, '
    'and assemble a dashboard — the hands-on side of the '
    '<strong>Unified Dashboards</strong> sprint.</div>'
    '<div style="margin-top:.5rem">'
    '<span class="pill">read-only · safe to explore</span>'
    '<span class="pill">saved to your profile</span></div>',
    unsafe_allow_html=True)
st.write("")

# ---- live KPIs + store bootstrap ----------------------------------------
try:
    ensure_store()
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

# ---- profile (identity that owns everything below) -----------------------
with st.sidebar:
    st.markdown("### Your profile")
    st.caption("Your dashboards and editor state are saved under this name and "
               "survive a container power-down. Type a new name to start fresh.")
    if "profile" not in st.session_state:
        existing = list_profiles()
        st.session_state.profile = existing[0] if existing else "me"
    profile = st.text_input("Profile name", value=st.session_state.profile).strip() or "me"
    if profile != st.session_state.profile:
        st.session_state.profile = profile
        st.session_state.pop("sql", None)  # reload editor state for the new profile
        st.rerun()
    others = [p for p in list_profiles() if p != profile]
    if others:
        st.caption("Also saved here: " + ", ".join(others[:8]))

# Restore the editor state for this profile (once per profile switch).
if "sql" not in st.session_state:
    ws = load_workspace(profile)
    st.session_state.sql = ws["sql"] if ws else _EXAMPLES["Revenue by category"]
    st.session_state.ws = ws or {}

st.divider()
left, right = st.columns([2, 3], gap="large")

# ---- builder: query -------------------------------------------------------
with left:
    st.subheader("1 · Query")
    st.caption("Start from an example, or write your own (read-only):")
    ex_cols = st.columns(2)
    for i, (name, sql) in enumerate(_EXAMPLES.items()):
        if ex_cols[i % 2].button(name, use_container_width=True, key=f"ex-{name}"):
            st.session_state.sql = sql
            st.rerun()
    st.session_state.sql = st.text_area(
        "SQL", value=st.session_state.sql, height=150, label_visibility="collapsed")

# ---- builder: chart (errors scoped here — the saved dashboard still renders) --
_ws = st.session_state.get("ws", {})
with right:
    st.subheader("2 · Chart")
    df = None
    try:
        df = run_readonly(st.session_state.sql)
    except Exception as exc:  # noqa: BLE001 - the learner's SQL; show it kindly
        st.error(f"Query error: {exc}")

    kind = x = y = title = None
    if df is not None and df.empty:
        st.info("Query returned no rows.")
    elif df is not None:
        cols = list(df.columns)
        cfg = st.columns(3)
        kinds = ["Bar", "Line", "Area", "Scatter", "Pie", "Table"]
        kind = cfg[0].selectbox(
            "Type", kinds, index=kinds.index(_ws.get("kind")) if _ws.get("kind") in kinds else 0)
        is_table = kind == "Table"
        x_lbl, y_lbl = ("Category", "Value") if kind == "Pie" else ("X / label", "Y / value")
        if is_table:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            x = cfg[1].selectbox(x_lbl, cols,
                                 index=cols.index(_ws["x"]) if _ws.get("x") in cols else 0)
            y = cfg[2].selectbox(y_lbl, cols, index=(
                cols.index(_ws["y"]) if _ws.get("y") in cols else min(1, len(cols) - 1)))
            if kind == "Pie" and df[x].nunique() > 8:
                st.caption("⚠ That's a lot of slices — a bar or table usually reads better.")
            st.plotly_chart(make_chart(df, kind, x, y), use_container_width=True)
        title = st.text_input("Chart title",
                              value=(f"{y} by {x}" if not is_table else "Data table"))
        if st.button("➕ Add to my dashboard", type="primary"):
            add_chart(profile, {"title": title, "sql": st.session_state.sql,
                                "kind": kind, "x": x, "y": y})
            st.success(f"Added “{title}”.")

# Persist the current editor state so returning lands exactly here.
save_workspace(profile, st.session_state.sql, kind, x, y, title)
st.session_state.ws = {"kind": kind, "x": x, "y": y, "title": title}

# ---- AI tutor (optional, alongside the deterministic builder) ------------
if anthropic is not None and os.environ.get("ANTHROPIC_API_KEY"):
    with st.expander("🎓 AI tutor — ask about your query, results, or what to try next"):
        st.caption("An optional guide alongside the builder. It sees your current "
                   "query and a sample of the results, and teaches by doing.")
        q = None
        tc = st.columns(3)
        if tc[0].button("Explain this query"):
            q = "Explain in plain language what this SQL query does, step by step."
        if tc[1].button("Why these results?"):
            q = "Explain what the returned rows show and any patterns a learner should notice."
        if tc[2].button("Suggest a chart"):
            q = ("Given these columns and rows, recommend the best chart type and which "
                 "columns to use for X and Y (or category/value), and briefly why.")
        typed = st.text_input("Or ask your own question", key="tutor_q")
        if st.button("Ask the tutor") and typed.strip():
            q = typed.strip()

        if q:
            sample = df.head(15).to_csv(index=False) if df is not None else "(no result set)"
            cols_desc = ", ".join(df.columns) if df is not None else "(none)"
            system = (
                "You are a warm, concise data-engineering tutor embedded in a BI "
                "dashboard builder. The learner practices SQL and dashboarding on a "
                "Postgres warehouse (schema `raw` with tables orders, customers). "
                "Teach by doing: give short, concrete explanations and one clear next "
                "step. Prefer plain language over jargon. Keep it under ~180 words.")
            prompt = (f"Learner's current SQL:\n```sql\n{st.session_state.sql}\n```\n\n"
                      f"Result columns: {cols_desc}\n"
                      f"Sample rows (CSV, first 15):\n{sample}\n\n"
                      f"Question: {q}")
            try:
                client = anthropic.Anthropic()
                with client.messages.stream(
                    model=TUTOR_MODEL, max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    st.session_state.tutor_answer = st.write_stream(stream.text_stream)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Tutor unavailable ({exc.__class__.__name__}). Check "
                         "ANTHROPIC_API_KEY, then try again.")
        elif st.session_state.get("tutor_answer"):
            st.markdown(st.session_state.tutor_answer)

# ---- the assembled dashboard (loaded from the durable store) -------------
st.divider()
dashboard = load_dashboard(profile)
head = st.columns([4, 1])
head[0].header(f"3 · Your dashboard · {len(dashboard)} chart(s)")
if dashboard and head[1].button("Clear all"):
    clear_dashboard(profile)
    st.rerun()

if not dashboard:
    st.caption("Build a chart above and click **Add to my dashboard** — your charts "
               "collect here and are saved to your profile, ready when you return.")
else:
    grid = st.columns(2, gap="large")
    for i, ch in enumerate(dashboard):
        with grid[i % 2].container(border=True):
            top = st.columns([5, 1])
            top[0].markdown(f"**{ch['title']}**")
            if top[1].button("🗑", key=f"rm-{ch['id']}", help="Remove"):
                remove_chart(ch["id"])
                st.rerun()
            try:
                d = run_readonly(ch["sql"])
                if ch["kind"] == "Table":
                    st.dataframe(d, use_container_width=True, hide_index=True)
                else:
                    st.plotly_chart(make_chart(d, ch["kind"], ch["x"], ch["y"]),
                                    use_container_width=True, key=f"ch-{ch['id']}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Couldn't render: {exc}")
