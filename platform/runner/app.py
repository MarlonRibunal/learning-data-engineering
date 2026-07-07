"""Streamlit lesson-runner — the local web app.

Run it from the repo root:

    streamlit run platform/runner/app.py
    # or: ./platform.sh runner

A thin shell over the grader: the sidebar groups tasks by sprint with live state,
the main pane shows the lesson + an in-browser editor, and "Check my work" calls
the same ``run_check`` the CLI uses. Runs on the host so it can reach the stack;
no hosting, no login.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

# Make the `grader` package importable when run via `streamlit run`.
_PLATFORM_DIR = Path(__file__).resolve().parents[1]
if str(_PLATFORM_DIR) not in sys.path:
    sys.path.insert(0, str(_PLATFORM_DIR))

import streamlit as st  # noqa: E402

from grader import Status, discover_tasks, next_task, run_check, start  # noqa: E402
from grader.core import default_tasks_root  # noqa: E402
from grader.progress import load as load_progress  # noqa: E402
from grader.spec import SpecError, TaskSpec, load_spec  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = REPO_ROOT / "docs" / "cheatsheets" / "glossary.md"
HOME = ("__home__", None)

_REAL_INFRA_CHECKS = {"sql_assert", "dbt_test", "airflow"}
_SPRINT_LABELS = {
    "sql-fundamentals": "SQL Fundamentals",
    "ingestion": "Ingestion",
    "data-quality": "Data Quality",
    "sprint-2-dbt": "Sprint 2 · dbt",
    "sprint-3-airflow": "Sprint 3 · Airflow",
    "serving": "Serving / BI",
    "streaming": "Streaming",
    "security": "Security",
    "architecture": "Architecture",
    "capstone": "Capstone",
}


# ---------- small helpers ----------
def _sprint_label(sprint: str) -> str:
    return _SPRINT_LABELS.get(sprint, sprint.replace("-", " ").title())


def _language_for(path: str) -> str:
    if path.endswith(".sql"):
        return "sql"
    if path.endswith(".py"):
        return "python"
    return "text"


def _load_sprint_intro(sprint: str) -> str | None:
    intro = default_tasks_root(REPO_ROOT) / sprint / "intro.md"
    return intro.read_text() if intro.is_file() else None


def _needs_stack(spec: TaskSpec) -> bool:
    if spec.reseed:
        return True
    return any(c.get("type") in _REAL_INFRA_CHECKS for c in spec.checks)


def _stack_up() -> bool:
    """Cheap best-effort check: is Postgres reachable on localhost:5432?"""
    try:
        with socket.create_connection(("127.0.0.1", 5432), timeout=0.3):
            return True
    except OSError:
        return False


def _task_state(sprint: str, task: str, progress: dict) -> str:
    """One of: pass, fail, error, in-progress, new."""
    status = progress.get(sprint, {}).get(task, {}).get("status")
    if status in ("pass", "fail", "error"):
        return status
    try:
        spec = load_spec(sprint, task, default_tasks_root(REPO_ROOT))
        if (REPO_ROOT / spec.submission_path).exists():
            return "in-progress"
    except SpecError:
        pass
    return "new"


_STATE_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️",
               "in-progress": "✏️", "new": "⬜"}
_STATE_PILL = {
    "pass": ("done", "Passed"),
    "fail": ("fail", "Try again"),
    "error": ("wip", "Could not run"),
    "in-progress": ("wip", "In progress"),
    "new": ("new", "Not started"),
}


def _task_header(sprint: str, task: str, spec, state: str) -> str:
    cls, label = _STATE_PILL.get(state, ("new", "Not started"))
    return (
        '<div class="task-head">'
        f'<div class="task-crumb">{_sprint_label(sprint)}</div>'
        '<div class="task-titlebar">'
        f'<span class="task-title">{spec.title}</span>'
        f'<span class="pill {cls}">{label}</span>'
        "</div></div>"
    )

# The curriculum as the data-engineering lifecycle: (sprint, lifecycle role).
_JOURNEY = [
    ("sql-fundamentals", "Query"),
    ("ingestion", "Ingestion"),
    ("sprint-2-dbt", "Transform"),
    ("data-quality", "Validate"),
    ("sprint-3-airflow", "Orchestrate"),
    ("serving", "Serve"),
    ("streaming", "Stream"),
    ("security", "Secure"),
    ("architecture", "Design"),
    ("capstone", "Capstone"),
]

# Tables to sample in a task's lesson pane, by sprint (spec `preview` overrides).
_SPRINT_PREVIEW = {
    "sql-fundamentals": ["orders", "customers"],
    "ingestion": ["landing.products_raw", "raw.products"],
}


def _sprint_counts(tasks, progress) -> dict[str, list[int]]:
    counts: dict[str, list[int]] = {}
    for sprint, task in tasks:
        c = counts.setdefault(sprint, [0, 0])
        c[1] += 1
        if progress.get(sprint, {}).get(task, {}).get("status") == "pass":
            c[0] += 1
    return counts


def _journey_html(tasks, progress) -> str:
    """A styled HTML journey stepper: lifecycle stages coloured by progress."""
    counts = _sprint_counts(tasks, progress)
    cells = []
    for sprint, role in _JOURNEY:
        if sprint not in counts:
            continue
        done, total = counts[sprint]
        state = "done" if total and done == total else ("wip" if done else "todo")
        pct = int(round(100 * done / total)) if total else 0
        cells.append(
            f'<div class="stage {state}">'
            f'<div class="stage-role">{role}</div>'
            f'<div class="stage-name">{_sprint_label(sprint)}</div>'
            f'<div class="stage-bar"><span style="width:{pct}%"></span></div>'
            f'<div class="stage-count">{done}/{total}</div>'
            f"</div>"
        )
    return f'<div class="journey">{"".join(cells)}</div>'


def _hero(done: int, total: int) -> str:
    pct = int(round(100 * done / total)) if total else 0
    return (
        '<div class="hero">'
        '<div class="hero-title">Learn data engineering by <em>doing</em></div>'
        '<div class="hero-sub">Write real SQL, dbt, Airflow and streaming code. Every task is '
        'graded against the <b>real stack</b> — not a simulation — from your first '
        '<code>SELECT</code> to a verified end-to-end pipeline.</div>'
        f'<div class="hero-meter"><div class="hero-meter-fill" style="width:{pct}%"></div></div>'
        f'<div class="hero-meta">{done} of {total} tasks passed · {pct}%</div>'
        "</div>"
    )


_CSS = """
<style>
:root{
  --brand:#4f46e5; --brand-d:#4338ca; --ink:#0f172a; --muted:#64748b;
  --line:#e2e8f0; --surface:#ffffff; --soft:#f8fafc;
  --green:#16a34a; --green-bg:#dcfce7; --amber:#d97706; --amber-bg:#fef3c7;
}
/* hide Streamlit chrome for a product feel */
header[data-testid="stHeader"]{display:none;}
[data-testid="stToolbar"]{display:none;}
.stApp{background:var(--soft);}
[data-testid="stMainBlockContainer"]{padding-top:2.2rem; max-width:1150px;}
html,body,[class*="css"]{font-feature-settings:"cv02","cv03","cv04";}
h1,h2,h3{color:var(--ink); letter-spacing:-.02em; font-weight:750;}
h2{margin-top:.4rem;}
a{color:var(--brand);}

/* ---- hero ---- */
.hero{background:linear-gradient(135deg,#eef2ff 0%,#faf5ff 100%);
  border:1px solid var(--line); border-radius:18px; padding:26px 28px; margin-bottom:20px;}
.hero-title{font-size:2rem; font-weight:800; letter-spacing:-.03em; color:var(--ink);}
.hero-title em{color:var(--brand); font-style:normal;}
.hero-sub{color:#475569; margin-top:8px; max-width:720px; line-height:1.5;}
.hero-sub code{background:#fff; border:1px solid var(--line); border-radius:6px; padding:1px 6px; color:var(--brand-d);}
.hero-meter{height:8px; background:#e0e7ff; border-radius:999px; margin-top:18px; overflow:hidden;}
.hero-meter-fill{height:100%; background:linear-gradient(90deg,var(--brand),#7c3aed); border-radius:999px;}
.hero-meta{color:var(--muted); font-size:.82rem; margin-top:8px; font-weight:600;}

/* ---- journey stepper ---- */
.journey{display:flex; gap:10px; overflow-x:auto; padding:6px 2px 12px; margin-bottom:6px;}
.stage{flex:1 0 118px; background:var(--surface); border:1px solid var(--line);
  border-radius:14px; padding:12px 12px 11px; position:relative;}
.stage:not(:last-child)::after{content:"›"; position:absolute; right:-11px; top:50%;
  transform:translateY(-50%); color:#cbd5e1; font-size:20px; font-weight:700;}
.stage-role{font-size:.62rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);}
.stage-name{font-size:.82rem; font-weight:700; color:var(--ink); margin-top:3px; line-height:1.15; min-height:2.1em;}
.stage-bar{height:5px; background:#eef2f7; border-radius:999px; margin-top:8px; overflow:hidden;}
.stage-bar span{display:block; height:100%; border-radius:999px; background:var(--brand);}
.stage-count{font-size:.72rem; color:var(--muted); font-weight:700; margin-top:6px;}
.stage.done{border-color:#bbf7d0; background:linear-gradient(180deg,#f0fdf4,#fff);}
.stage.done .stage-bar span{background:var(--green);}
.stage.done .stage-count{color:var(--green);}
.stage.wip{border-color:#fde68a; background:linear-gradient(180deg,#fffbeb,#fff);}
.stage.wip .stage-bar span{background:var(--amber);}

/* ---- sidebar ---- */
[data-testid="stSidebar"]{background:#fff; border-right:1px solid var(--line);}
[data-testid="stSidebar"] .brand{font-weight:800; font-size:1.05rem; letter-spacing:-.02em;
  color:var(--ink); padding:2px 4px 2px; display:flex; align-items:center; gap:8px;}
[data-testid="stSidebar"] .grp{font-size:.66rem; font-weight:800; letter-spacing:.09em;
  text-transform:uppercase; color:var(--muted); margin:14px 6px 4px;}
[data-testid="stSidebar"] .stButton>button{border:none; background:transparent; color:#334155;
  text-align:left; justify-content:flex-start; font-weight:600; padding:6px 10px; border-radius:9px;
  box-shadow:none;}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--soft); color:var(--ink);}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]{background:var(--brand)!important;
  color:#fff!important;}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover{background:var(--brand-d)!important;}

/* ---- buttons (main) ---- */
.stButton>button{border-radius:10px; font-weight:650; border:1px solid var(--line);}
[data-testid="stBaseButton-primary"]{background:var(--brand); border:none; box-shadow:0 1px 2px rgba(79,70,229,.35);}
[data-testid="stBaseButton-primary"]:hover{background:var(--brand-d);}

/* ---- cards / expanders / inputs ---- */
[data-testid="stExpander"]{border:1px solid var(--line); border-radius:12px; background:#fff;}
[data-testid="stExpander"] summary{font-weight:650;}
[data-testid="stProgress"] > div > div > div{background:linear-gradient(90deg,var(--brand),#7c3aed);}
[data-testid="stDataFrame"]{border:1px solid var(--line); border-radius:10px; overflow:hidden;}
textarea{border-radius:10px!important; font-family:"SF Mono",ui-monospace,Menlo,monospace!important;}
[data-testid="stAlert"]{border-radius:12px;}
.stCode{border-radius:10px;}

/* ---- task header + status pill ---- */
.task-head{margin:2px 0 14px;}
.task-crumb{font-size:.68rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--brand);}
.task-titlebar{display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-top:4px;}
.task-title{font-size:1.7rem; font-weight:800; letter-spacing:-.03em; color:var(--ink); line-height:1.1;}
.pill{font-size:.72rem; font-weight:800; padding:3px 11px; border-radius:999px; letter-spacing:.02em; white-space:nowrap;}
.pill.done{background:var(--green-bg); color:#166534;}
.pill.fail{background:#fee2e2; color:#b91c1c;}
.pill.wip{background:var(--amber-bg); color:#92400e;}
.pill.new{background:#eef2f7; color:var(--muted);}
/* content section headers inside the cards */
.sec{font-size:.7rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0 0 6px;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px;}
</style>
"""


def _inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def _to_records(res) -> list[dict]:
    from decimal import Decimal

    def cell(v):
        if isinstance(v, Decimal):
            return float(v)
        if isinstance(v, (int, float, str, type(None))):
            return v
        return str(v)

    return [{c: cell(v) for c, v in zip(res.columns, row)} for row in res.rows]


def _preview_tables(sprint: str, spec) -> list[str]:
    return spec.preview or _SPRINT_PREVIEW.get(sprint, [])


def _safe_preview(table: str, seed: bool):
    from grader.context import InfraError
    from grader.playground import run_sql

    try:
        res = run_sql(REPO_ROOT, f"SELECT * FROM {table} LIMIT 5", seed=seed)
    except InfraError:
        return None
    if res.error or not res.rows:
        return None
    return _to_records(res)


# ---------- main ----------
def main() -> None:
    st.set_page_config(page_title="Learn Data Engineering", page_icon="🧪", layout="wide")
    _inject_css()
    if "sel" not in st.session_state:
        st.session_state.sel = HOME

    tasks = discover_tasks(REPO_ROOT)
    progress = load_progress(REPO_ROOT)
    sel = st.session_state.sel

    st.sidebar.markdown('<div class="brand">🧪 Learn by doing</div>', unsafe_allow_html=True)
    if not tasks:
        st.sidebar.info("No tasks found yet.")
        st.title("No tasks found")
        st.write("Add a task under `projects/datamart-intelligence-platform/tasks/`.")
        return

    done = sum(1 for s, t in tasks if progress.get(s, {}).get(t, {}).get("status") == "pass")

    if st.sidebar.button("🏠  Home", use_container_width=True,
                         type="primary" if sel == HOME else "secondary"):
        st.session_state.sel = HOME
    st.sidebar.progress(done / len(tasks), text=f"{done}/{len(tasks)} passed")

    current_sprint = None
    for sprint, task in tasks:
        if sprint != current_sprint:
            st.sidebar.markdown(f'<div class="grp">{_sprint_label(sprint)}</div>',
                                unsafe_allow_html=True)
            current_sprint = sprint
        icon = _STATE_ICON[_task_state(sprint, task, progress)]
        if st.sidebar.button(f"{icon}  {task}", key=f"nav-{sprint}-{task}",
                             use_container_width=True,
                             type="primary" if sel == (sprint, task) else "secondary"):
            st.session_state.sel = (sprint, task)

    sel_sprint, sel_task = st.session_state.sel
    if sel_sprint == HOME[0]:
        _render_home(tasks, progress, done)
    else:
        _render_task(sel_sprint, sel_task, progress)


def _render_home(tasks, progress, done) -> None:
    st.markdown(_hero(done, len(tasks)), unsafe_allow_html=True)
    st.markdown('<div class="grp" style="margin:6px 2px 8px">'
                'Your journey through the data engineering lifecycle</div>',
                unsafe_allow_html=True)
    st.markdown(_journey_html(tasks, progress), unsafe_allow_html=True)

    nxt = next_task(REPO_ROOT)
    if nxt:
        if st.button(f"▶ Continue: {_sprint_label(nxt[0])} · {nxt[1]}", type="primary"):
            st.session_state.sel = nxt
            st.rerun()
    else:
        st.success("🎉 You've passed every task. Nice work!")

    if not _stack_up():
        st.warning("The data stack looks **down**. Real-infra tasks need it — start with "
                   "`./platform.sh up` (or `docker compose up -d`).")

    if GLOSSARY.is_file():
        with st.expander("📖 Glossary — data engineering terms"):
            st.markdown(GLOSSARY.read_text())

    st.divider()
    current_sprint = None
    for sprint, task in tasks:
        if sprint != current_sprint:
            st.subheader(_sprint_label(sprint))
            intro = _load_sprint_intro(sprint)
            if intro:
                st.caption(intro)
            current_sprint = sprint
        icon = _STATE_ICON[_task_state(sprint, task, progress)]
        st.markdown(f"{icon}  {task}")


def _render_task(sprint, task, progress) -> None:
    try:
        spec = load_spec(sprint, task, default_tasks_root(REPO_ROOT))
    except SpecError as exc:
        st.error(f"Task spec error: {exc}")
        return

    state = _task_state(sprint, task, progress)
    st.markdown(_task_header(sprint, task, spec, state), unsafe_allow_html=True)

    if _needs_stack(spec) and not _stack_up():
        st.warning("The data stack looks **down**, so checks will report *could not run* "
                   "(not a wrong answer). Start it: `./platform.sh up`.")

    submission = REPO_ROOT / spec.submission_path
    lang = _language_for(spec.submission_path)
    col_lesson, col_work = st.columns([1, 1], gap="large")

    with col_lesson:
        with st.container(border=True):
            st.markdown('<div class="sec">📖 Lesson</div>', unsafe_allow_html=True)
            lesson_file = spec.task_dir / "lesson.md"
            if lesson_file.is_file():
                st.markdown(lesson_file.read_text())
            elif spec.scaffold:
                st.markdown("Read the scaffold, then write your solution.")
                st.code((spec.task_dir / spec.scaffold).read_text(), language=lang)
            else:
                st.info("No lesson text for this task yet.")

            intro = _load_sprint_intro(sprint)
            if intro:
                with st.expander(f"About {_sprint_label(sprint)}"):
                    st.markdown(intro)

            preview = _preview_tables(sprint, spec)
            if preview and _stack_up():
                with st.expander("📋 Peek at the data"):
                    for i, table in enumerate(preview):
                        st.caption(f"`{table}`")
                        records = _safe_preview(table, seed=(i == 0))
                        if records:
                            st.dataframe(records, use_container_width=True, hide_index=True)
                        else:
                            st.caption("_(empty or unavailable)_")

    with col_work:
        with st.container(border=True):
            st.markdown('<div class="sec">⌨️ Your work</div>', unsafe_allow_html=True)
            if not submission.exists():
                st.info("You haven't started this task yet.")
                if spec.scaffold and st.button("▶  Start this task", type="primary",
                                               use_container_width=True):
                    start(sprint, task, REPO_ROOT, overwrite=False)
                    st.rerun()
            else:
                current = submission.read_text()
                edited = st.text_area("Edit your submission", value=current, height=260,
                                      key=f"editor-{sprint}-{task}",
                                      label_visibility="collapsed")
                with st.expander("Preview (syntax-highlighted)"):
                    st.code(edited, language=lang)

                # Live SQL playground for plain SQL (not dbt/jinja models).
                if lang == "sql" and "{{" not in edited:
                    if st.button("▶  Run query", use_container_width=True,
                                 help="Run it against the warehouse and see the rows"):
                        _run_playground(edited)

                if st.button("✅  Check my work", type="primary", use_container_width=True):
                    submission.write_text(edited)
                    result = run_check(sprint, task, REPO_ROOT, make_proof=True)
                    _render_result(result)

                s1, s2 = st.columns(2)
                if s1.button("💾  Save", use_container_width=True):
                    submission.write_text(edited)
                    st.toast("Saved.")
                if spec.scaffold and s2.button("↺  Reset", use_container_width=True):
                    start(sprint, task, REPO_ROOT, overwrite=True)
                    st.rerun()

            if spec.solution:
                solution_file = spec.task_dir / spec.solution
                if solution_file.is_file():
                    with st.expander("😩 Stuck? Reveal a worked solution"):
                        st.caption("Try it yourself first — the struggle is where the "
                                   "learning happens. But a worked example beats staying stuck.")
                        st.code(solution_file.read_text(), language=lang)


def _run_playground(sql: str) -> None:
    from grader.context import InfraError
    from grader.playground import run_sql

    try:
        res = run_sql(REPO_ROOT, sql)
    except InfraError as exc:
        st.warning(f"Can't run — the stack looks down ({exc}). Start it: `./platform.sh up`.")
        return
    if res.error:
        st.error(res.error)
        return
    if not res.rows:
        st.info("Query ran successfully — 0 rows returned.")
        return
    st.dataframe(_to_records(res), use_container_width=True)
    st.caption(f"{len(res.rows)} row(s)" + (" (truncated)" if res.truncated else ""))


def _render_result(result) -> None:
    for check in result.checks:
        icon = _STATUS_ICON.get(check.status.value, "•")
        if check.status is Status.PASS:
            st.markdown(f"{icon} **{check.name}**")
        else:
            st.markdown(f"{icon} **{check.name}** — {check.hint}")
    if result.status is Status.PASS:
        st.success("PASS — nice work.")
        st.balloons()
        if result.proof_dir is not None:
            rel = result.proof_dir.relative_to(REPO_ROOT)
            st.info(f"🎉 Portfolio artifact written to `{rel}` — commit it to your "
                    f"GitHub to show what you built.")
            chart = result.proof_dir / "chart.png"
            if chart.is_file():
                st.image(str(chart))
    elif result.status is Status.ERROR:
        st.warning("Could not run — the stack looks unavailable (not your work). "
                   "Start it with `./platform.sh up` and try again.")
    else:
        st.error("Not yet — fix the items above and check again.")


_STATUS_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️"}


if __name__ == "__main__":
    main()
