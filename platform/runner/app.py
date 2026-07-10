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
    "sprint-4-spark": "Big Data · Spark",
    "sprint-5-hybrid-cloud": "Hybrid Cloud",
    "serving": "Serving / BI",
    "streaming": "Streaming",
    "sprint-8-realtime": "Real-time · Windows",
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


# Unified status dots (consistent shape, colour-coded like the rest of the UI):
# green = passed, amber = in progress, red = failed, orange = could-not-run, grey = new.
_STATE_ICON = {"pass": "🟢", "fail": "🔴", "error": "🟠",
               "in-progress": "🟡", "new": "⚪"}
_STATE_PILL = {
    "pass": ("done", "Passed"),
    "fail": ("fail", "Try again"),
    "error": ("wip", "Could not run"),
    "in-progress": ("wip", "In progress"),
    "new": ("new", "Not started"),
}


def _task_header(sprint: str, task: str, spec, state: str,
                 level: int = 0, total: int = 0) -> str:
    cls, label = _STATE_PILL.get(state, ("new", "Not started"))
    crumb = _sprint_label(sprint)
    if level and total:
        crumb = f"Level {level} of {total} · {crumb}"
    return (
        '<div class="task-head">'
        f'<div class="task-crumb">{crumb}</div>'
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
    ("sprint-4-spark", "Process"),
    ("sprint-5-hybrid-cloud", "Hybrid"),
    ("serving", "Serve"),
    ("streaming", "Stream"),
    ("sprint-8-realtime", "Real-time"),
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


def _res_key(sprint, task) -> str:
    return f"_res::{sprint}::{task}"


def _next_in_sequence(tasks, sprint, task):
    """The task immediately after (sprint, task) in curriculum order, or None."""
    for i, (s, t) in enumerate(tasks):
        if (s, t) == (sprint, task):
            return tasks[i + 1] if i + 1 < len(tasks) else None
    return None


def _level_of(tasks, sprint, task) -> int:
    """1-based position of (sprint, task) in the linear path (0 if not found)."""
    for i, (s, t) in enumerate(tasks):
        if (s, t) == (sprint, task):
            return i + 1
    return 0


def _current_sprint(tasks, progress) -> str | None:
    """The sprint the learner is 'on' — the sprint of the next unpassed task."""
    for sprint, task in tasks:
        if progress.get(sprint, {}).get(task, {}).get("status") != "pass":
            return sprint
    return tasks[-1][0] if tasks else None


def _frontier_index(tasks, progress) -> int:
    """Index of the first unpassed task — the furthest the learner may reach.

    Everything up to and including this index is unlocked; anything after it
    is locked until the levels in front are cleared. If every task is passed,
    the frontier is past the end (nothing locked).
    """
    for i, (sprint, task) in enumerate(tasks):
        if progress.get(sprint, {}).get(task, {}).get("status") != "pass":
            return i
    return len(tasks)


def _is_locked(tasks, progress, sprint, task) -> bool:
    """A level is locked until every level ahead of it in the path is passed.

    An already-passed level is never locked, even if the learner cleared it
    out of order — you don't re-lock work that's done.
    """
    if progress.get(sprint, {}).get(task, {}).get("status") == "pass":
        return False
    return _level_of(tasks, sprint, task) - 1 > _frontier_index(tasks, progress)


def _grouped_by_sprint(tasks):
    """Yield (sprint, [tasks...]) preserving curriculum order."""
    order, groups = [], {}
    for sprint, task in tasks:
        if sprint not in groups:
            order.append(sprint)
            groups[sprint] = []
        groups[sprint].append(task)
    return [(s, groups[s]) for s in order]


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
/* Strip the deploy/menu chrome for a product feel — but hide only the
   toolbar ACTIONS, not the toolbar itself: Streamlit nests the
   re-open-sidebar button inside stToolbar, so hiding the whole toolbar
   traps a collapsed sidebar shut. */
header[data-testid="stHeader"]{background:transparent; box-shadow:none;}
[data-testid="stAppDeployButton"]{display:none;}
[data-testid="stMainMenu"]{display:none;}
[data-testid="stStatusWidget"]{display:none;}
[data-testid="stDecoration"]{display:none;}
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
/* sprint groups: compact single-line headers so long names don't wrap */
[data-testid="stSidebar"] [data-testid="stExpander"] summary{padding:6px 8px;}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p{font-size:.85rem!important;
  font-weight:750; letter-spacing:-.015em; margin:0; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis;}

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

/* ---- level-cleared moment ---- */
.cleared{background:linear-gradient(135deg,#f0fdf4 0%,#ecfeff 100%);
  border:1px solid #bbf7d0; border-radius:14px; padding:16px 18px; margin:14px 0 10px;}
.cleared-badge{font-size:1.15rem; font-weight:850; letter-spacing:-.02em; color:#15803d;}
.cleared-meta{color:#3f6212; font-size:.84rem; font-weight:650; margin-top:2px;}
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

    # A calm map: completed sprints collapse to a checkmark, the sprint you're
    # on is open, upcoming ones stay tucked away — so the whole 34-task
    # curriculum never shouts at once.
    on_sprint = _current_sprint(tasks, progress)
    nxt = next_task(REPO_ROOT)  # the single "you are here" task
    sel_sprint_now = sel[0] if sel != HOME else None
    for sprint, sprint_tasks in _grouped_by_sprint(tasks):
        c_done = sum(1 for t in sprint_tasks
                     if progress.get(sprint, {}).get(t, {}).get("status") == "pass")
        c_total = len(sprint_tasks)
        complete = c_done == c_total
        # A whole sprint is locked when even its first level is out of reach.
        sprint_locked = _is_locked(tasks, progress, sprint, sprint_tasks[0])
        if complete:
            badge = "✅"                       # every level cleared
        elif sprint == on_sprint:
            badge = "🔵"                       # the sprint you're on
        elif c_done:
            badge = "🟡"                       # partway in — momentum
        elif sprint_locked:
            badge = "🔒"                       # not yet — finish the levels ahead
        else:
            badge = "⚪"                       # not started
        header = f"{badge} {_sprint_label(sprint)} · {c_done}/{c_total}"
        # Open the sprint you're on, or one you've navigated into.
        expanded = sprint in (on_sprint, sel_sprint_now)
        with st.sidebar.expander(header, expanded=expanded):
            for task in sprint_tasks:
                locked = _is_locked(tasks, progress, sprint, task)
                icon = "🔒" if locked else _STATE_ICON[_task_state(sprint, task, progress)]
                here = "  ◄" if (sprint, task) == nxt else ""
                if st.button(f"{icon}  {task}{here}", key=f"nav-{sprint}-{task}",
                             use_container_width=True, disabled=locked,
                             help="Locked — finish the levels ahead first" if locked else None,
                             type="primary" if sel == (sprint, task) else "secondary"):
                    st.session_state.sel = (sprint, task)

    sel_sprint, sel_task = st.session_state.sel
    if sel_sprint == HOME[0]:
        _render_home(tasks, progress, done)
    else:
        _render_task(sel_sprint, sel_task, progress, tasks)


def _render_home(tasks, progress, done) -> None:
    st.markdown(_hero(done, len(tasks)), unsafe_allow_html=True)
    st.markdown('<div class="grp" style="margin:6px 2px 8px">'
                'Your journey through the data engineering lifecycle</div>',
                unsafe_allow_html=True)
    st.markdown(_journey_html(tasks, progress), unsafe_allow_html=True)

    nxt = next_task(REPO_ROOT)
    if nxt:
        level = _level_of(tasks, *nxt)
        label = "▶ Start learning" if done == 0 else f"▶ Continue at level {level}"
        st.caption(f"Next up: **{_sprint_label(nxt[0])} · {nxt[1]}**")
        if st.button(label, type="primary", use_container_width=True):
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


def _render_task(sprint, task, progress, tasks) -> None:
    try:
        spec = load_spec(sprint, task, default_tasks_root(REPO_ROOT))
    except SpecError as exc:
        st.error(f"Task spec error: {exc}")
        return

    state = _task_state(sprint, task, progress)
    level, total = _level_of(tasks, sprint, task), len(tasks)
    st.markdown(_task_header(sprint, task, spec, state, level, total),
                unsafe_allow_html=True)

    # Locked: the learner jumped ahead. Show a gate, not the editor, and point
    # them back to where they left off.
    if _is_locked(tasks, progress, sprint, task):
        nxt = next_task(REPO_ROOT)
        with st.container(border=True):
            st.markdown('<div class="sec">🔒 Locked</div>', unsafe_allow_html=True)
            st.write("Finish the levels ahead of this one first — the path is meant "
                     "to be walked in order, so each level builds on the last.")
            if nxt and st.button(f"▶ Go to level {_level_of(tasks, *nxt)} · {nxt[1]}",
                                 type="primary"):
                st.session_state.sel = nxt
                st.rerun()
        return

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
                edited = st.text_area("Edit your submission", value=current, height=280,
                                      key=f"editor-{sprint}-{task}",
                                      label_visibility="collapsed")

                # One hero action. Checking always saves first — no separate step.
                if st.button("✓  Check my work", type="primary", use_container_width=True):
                    submission.write_text(edited)
                    result = run_check(sprint, task, REPO_ROOT, make_proof=True)
                    st.session_state[_res_key(sprint, task)] = result
                    st.session_state["_just_checked"] = (sprint, task)
                    st.rerun()

                # Everything else is secondary and quiet — one row, no shouting.
                can_run = lang == "sql" and "{{" not in edited
                cols = st.columns(3 if can_run else 2)
                i = 0
                if can_run:
                    if cols[i].button("▶ Run", use_container_width=True,
                                      help="Run this query against the warehouse"):
                        submission.write_text(edited)
                        st.session_state[_res_key(sprint, task)] = None
                        _run_playground(edited)
                    i += 1
                if cols[i].button("💾 Save", use_container_width=True):
                    submission.write_text(edited)
                    st.toast("Saved.")
                i += 1
                if spec.scaffold and cols[i].button("↺ Reset", use_container_width=True):
                    start(sprint, task, REPO_ROOT, overwrite=True)
                    st.session_state.pop(_res_key(sprint, task), None)
                    st.rerun()

            if spec.solution:
                solution_file = spec.task_dir / spec.solution
                if solution_file.is_file():
                    with st.expander("😩 Stuck? Reveal a worked solution"):
                        st.caption("Try it yourself first — the struggle is where the "
                                   "learning happens. But a worked example beats staying stuck.")
                        st.code(solution_file.read_text(), language=lang)

    # The last check result lives below the cards and survives reruns, so the
    # "Level cleared → Next level" moment persists until the learner moves on.
    stored = st.session_state.get(_res_key(sprint, task))
    if stored is not None:
        just = st.session_state.pop("_just_checked", None) == (sprint, task)
        _render_result(stored, sprint, task, tasks, celebrate=just)


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


def _render_result(result, sprint, task, tasks, celebrate=False) -> None:
    for check in result.checks:
        icon = _STATUS_ICON.get(check.status.value, "•")
        if check.status is Status.PASS:
            st.markdown(f"{icon} **{check.name}**")
        else:
            st.markdown(f"{icon} **{check.name}** — {check.hint}")

    if result.status is Status.PASS:
        _render_cleared(sprint, task, tasks, celebrate)
        if result.proof_dir is not None:
            rel = result.proof_dir.relative_to(REPO_ROOT)
            st.info(f"🏆 Portfolio artifact written to `{rel}` — commit it to your "
                    f"GitHub to show what you built.")
            chart = result.proof_dir / "chart.png"
            if chart.is_file():
                st.image(str(chart))
    elif result.status is Status.ERROR:
        st.warning("Could not run — the stack looks unavailable (not your work). "
                   "Start it with `./platform.sh up` and try again.")
    else:
        st.error("Not yet — fix the items above and check again.")


def _render_cleared(sprint, task, tasks, celebrate) -> None:
    """The 'level cleared → next level' moment. Balloons fire once, on the pass."""
    if celebrate:
        st.balloons()
    done = sum(1 for s, t in tasks
               if load_progress(REPO_ROOT).get(s, {}).get(t, {}).get("status") == "pass")
    nxt = _next_in_sequence(tasks, sprint, task)
    # Only announce a new stage when the next level actually crosses sprints.
    onto = f" · onto {_sprint_label(nxt[0])}" if nxt and nxt[0] != sprint else ""
    st.markdown(
        '<div class="cleared">'
        '<div class="cleared-badge">✦ Level cleared</div>'
        f'<div class="cleared-meta">{done} of {len(tasks)} done{onto}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    if nxt:
        if st.button(f"Next level → {nxt[1]}", type="primary",
                     use_container_width=True, key=f"next-{sprint}-{task}"):
            st.session_state.pop(_res_key(sprint, task), None)
            st.session_state.sel = nxt
            st.rerun()
    else:
        st.success("🎉 You've cleared the whole path — every level passed. Incredible.")


_STATUS_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️"}


if __name__ == "__main__":
    main()
