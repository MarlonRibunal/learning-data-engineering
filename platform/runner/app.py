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
    "sprint-9-dashboard": "Dashboards",
    "sprint-10-production": "Production & Career",
    "sprint-oncall": "On-Call Incident",
    "sprint-debug": "Debug the Pipeline",
    "sprint-migration": "Schema Migration",
    "sprint-advanced": "Advanced Challenges",
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
# Consistent Material line-icons for the sidebar nav (shape conveys state).
_STATE_MICON = {"pass": ":material/check_circle:", "fail": ":material/cancel:",
                "error": ":material/error:", "in-progress": ":material/pending:",
                "new": ":material/radio_button_unchecked:"}
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
        f'<div class="task-crumb">{_ICON["target"]}{crumb}</div>'
        '<div class="task-titlebar">'
        f'<span class="task-title">{spec.title}</span>'
        f'<span class="pill {cls}"><span class="dot"></span>{label}</span>'
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
    ("sprint-9-dashboard", "Dashboard"),
    ("security", "Secure"),
    ("architecture", "Design"),
    ("sprint-10-production", "Launch"),
    ("sprint-oncall", "On-Call"),
    ("sprint-debug", "Debug"),
    ("sprint-migration", "Migrate"),
    ("sprint-advanced", "Advanced"),
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{
  --bg:#f6f7f9; --panel:#ffffff; --panel-2:#fbfbfc;
  --line:#e7e8ec; --line-2:#eef0f3;
  --ink:#17181b; --muted:#6a6e77; --faint:#9297a0;
  /* Monochrome-forward: ink is the accent. Colour is reserved for status. */
  --accent:#1d1e21; --accent-h:#34363b; --accent-soft:#f0f1f3;
  --green:#3fa66a; --green-soft:#e9f5ee; --green-ink:#217a4b;
  --amber:#c88a1c; --amber-soft:#fbf1db; --amber-ink:#8a5d0e;
  --red:#d6494f; --red-soft:#fbe9ea; --red-ink:#a3323a;
  --r:12px; --r-sm:8px;
  --sh:0 1px 2px rgba(20,21,26,.04), 0 1px 3px rgba(20,21,26,.05);
}
/* Dark mode — follow the viewer's OS. The palette is monochrome, so this is a
   token flip: dark surfaces, light ink, colour reserved for status. */
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0f1011; --panel:#17181a; --panel-2:#1d1e21;
    --line:#282a2f; --line-2:#212327;
    --ink:#e7e8ea; --muted:#9a9ea6; --faint:#70747c;
    --accent:#e7e8ea; --accent-h:#c9cbcf; --accent-soft:#282a2f;
    --green:#4cb782; --green-soft:#16241d; --green-ink:#79d3a2;
    --amber:#d6a441; --amber-soft:#271f12; --amber-ink:#e2ba6c;
    --red:#e0575d; --red-soft:#291518; --red-ink:#ef8b90;
    --sh:0 1px 2px rgba(0,0,0,.3), 0 1px 3px rgba(0,0,0,.28);
    color-scheme:dark;
  }
  .stApp{background:var(--bg);}
  /* the primary CTA inverts: a light button with dark text (ink flipped) */
  [data-testid="stBaseButton-primary"]{color:#16171a!important;}
  [data-testid="stBaseButton-primary"] *{color:#16171a!important;}
  /* Streamlit paints these from its static light theme — repaint them dark. */
  [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="stExpander"]{background:var(--panel)!important;}
  [data-testid="stAlert"]{background:var(--panel-2)!important;}
  [data-testid="stAlert"] *{color:var(--ink)!important;}
  pre, code, .stCode, [data-testid="stCode"], [data-testid="stCode"] *{
    background:var(--panel-2)!important;}
  [data-testid="stCode"] code, [data-testid="stCode"] span{background:transparent!important;}
  [data-baseweb="textarea"], textarea{background:var(--panel-2)!important; color:var(--ink)!important;}
  /* Streamlit hard-codes a dark textColor — force our light ink on text nodes
     (targeted, so button/pill/chip colours are left alone). */
  [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
  [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
  [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] strong,
  [data-testid="stMarkdownContainer"] em, [data-testid="stMarkdownContainer"] td,
  [data-testid="stMarkdownContainer"] th, .task-title, .hero-title, .hero-sub,
  [data-testid="stExpander"] summary, [data-testid="stCaptionContainer"]{
    color:var(--ink)!important;}
  [data-testid="stMarkdownContainer"] code, code{color:var(--green-ink)!important;}
}
/* Strip the deploy/menu chrome — but keep the toolbar so the collapsed
   sidebar's re-open control stays reachable. */
header[data-testid="stHeader"]{background:transparent; box-shadow:none;}
[data-testid="stAppDeployButton"]{display:none;}
[data-testid="stMainMenu"]{display:none;}
[data-testid="stStatusWidget"]{display:none;}
[data-testid="stDecoration"]{display:none;}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-feature-settings:'cv02','cv03','cv04','cv11'; -webkit-font-smoothing:antialiased;}
.stApp{background:var(--bg);}
[data-testid="stMainBlockContainer"]{padding-top:2.4rem; max-width:1120px;}
h1,h2,h3{color:var(--ink); letter-spacing:-.021em; font-weight:650;}
h2{margin-top:.3rem;}
p,li,span{color:var(--ink);}
a{color:var(--accent); text-decoration:none;}
.icon{width:15px; height:15px; stroke:currentColor; fill:none; stroke-width:1.6;
  stroke-linecap:round; stroke-linejoin:round; flex:0 0 auto; vertical-align:-2px;}

/* ---- hero (bento) ---- */
.hero{background:var(--panel); border:1px solid var(--line); border-radius:16px;
  padding:24px 26px; margin-bottom:18px; box-shadow:var(--sh);}
.hero-title{font-size:1.7rem; font-weight:680; letter-spacing:-.03em; color:var(--ink);}
.hero-title em{color:var(--ink); font-style:normal; box-shadow:inset 0 -.42em 0 var(--accent-soft);}
.hero-sub{color:var(--muted); margin-top:7px; max-width:660px; line-height:1.55; font-size:.92rem;}
.hero-sub code{background:var(--panel-2); border:1px solid var(--line); border-radius:5px;
  padding:1px 5px; color:var(--accent-h); font-size:.85em;}
.hero-meter{height:6px; background:var(--line-2); border-radius:999px; margin-top:18px; overflow:hidden;}
.hero-meter-fill{height:100%; background:var(--accent); border-radius:999px;}
.hero-meta{color:var(--faint); font-size:.78rem; margin-top:8px; font-weight:500; letter-spacing:.01em;}

/* ---- journey (bento tiles) ---- */
.journey{display:flex; gap:8px; overflow-x:auto; padding:2px 2px 10px; margin-bottom:2px;}
.stage{flex:1 0 112px; background:var(--panel); border:1px solid var(--line);
  border-radius:12px; padding:12px 13px 11px; position:relative; box-shadow:var(--sh);}
.stage:not(:last-child)::after{content:""; position:absolute; right:-6px; top:50%; width:6px;
  height:1px; background:var(--line); transform:translateY(-50%);}
.stage-role{font-size:.6rem; font-weight:600; letter-spacing:.07em; text-transform:uppercase; color:var(--faint);}
.stage-name{font-size:.8rem; font-weight:600; color:var(--ink); margin-top:3px; line-height:1.2; min-height:2.1em; letter-spacing:-.01em;}
.stage-bar{height:4px; background:var(--line-2); border-radius:999px; margin-top:9px; overflow:hidden;}
.stage-bar span{display:block; height:100%; border-radius:999px; background:var(--accent);}
.stage-count{font-size:.7rem; color:var(--faint); font-weight:500; margin-top:7px;}
.stage.done{border-color:#cfe8da;}
.stage.done .stage-bar span{background:var(--green);}
.stage.done .stage-count{color:var(--green-ink);}
.stage.wip{border-color:#ecdcb4;}
.stage.wip .stage-bar span{background:var(--amber);}

/* ---- sidebar ---- */
[data-testid="stSidebar"]{background:var(--panel); border-right:1px solid var(--line);}
[data-testid="stSidebar"] .brand{font-weight:650; font-size:.98rem; letter-spacing:-.02em;
  color:var(--ink); padding:2px 4px; display:flex; align-items:center; gap:8px;}
[data-testid="stSidebar"] .brand .icon{width:17px; height:17px; color:var(--accent);}
[data-testid="stSidebar"] .grp{font-size:.64rem; font-weight:600; letter-spacing:.08em;
  text-transform:uppercase; color:var(--faint); margin:14px 6px 4px;}
[data-testid="stSidebar"] .stButton>button{border:none; background:transparent; color:var(--muted);
  text-align:left; justify-content:flex-start; font-weight:500; padding:5px 9px; border-radius:7px;
  box-shadow:none; font-size:.88rem; letter-spacing:-.01em; min-height:0;}
[data-testid="stSidebar"] .stButton>button:hover{background:var(--panel-2); color:var(--ink);}
[data-testid="stSidebar"] .stButton>button:disabled{color:var(--faint); opacity:.6;}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]{background:var(--accent-soft)!important;
  color:var(--accent-h)!important; font-weight:600!important;}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover{background:#e4e7fb!important;}
[data-testid="stSidebar"] [data-testid="stExpander"]{border:none; background:transparent;}
[data-testid="stSidebar"] [data-testid="stExpander"] summary{padding:6px 8px; border-radius:7px;}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover{background:var(--panel-2);}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p{font-size:.82rem!important;
  font-weight:600; letter-spacing:-.01em; margin:0; white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; color:var(--ink);}

/* ---- buttons (main) — Linear flat ---- */
.stButton>button{border-radius:8px; font-weight:550; border:1px solid var(--line);
  background:var(--panel); color:var(--ink); box-shadow:var(--sh); letter-spacing:-.01em;
  transition:background .12s,border-color .12s;}
.stButton>button:hover{border-color:#d7d9df; background:var(--panel-2);}
[data-testid="stBaseButton-primary"]{background:var(--accent)!important; border:1px solid var(--accent)!important;
  color:#fff!important; box-shadow:0 1px 2px rgba(20,21,26,.18);}
[data-testid="stBaseButton-primary"]:hover{background:var(--accent-h)!important; border-color:var(--accent-h)!important;}
/* button label + icon sit in child nodes — make them follow the button colour */
.stButton>button *{color:inherit!important;}

/* ---- cards / expanders / inputs ---- */
[data-testid="stExpander"]{border:1px solid var(--line); border-radius:10px; background:var(--panel); box-shadow:none;}
[data-testid="stExpander"] summary{font-weight:550; font-size:.9rem; color:var(--ink);}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px; border-color:var(--line)!important;}
[data-testid="stProgress"] > div > div > div{background:var(--accent);}
[data-testid="stDataFrame"]{border:1px solid var(--line); border-radius:9px; overflow:hidden;}
textarea{border-radius:9px!important; font-family:'SF Mono',ui-monospace,Menlo,monospace!important;
  font-size:.86rem!important; border-color:var(--line)!important; background:var(--panel-2)!important;}
[data-testid="stAlert"]{border-radius:10px; border:1px solid var(--line);}
.stCode{border-radius:9px;}
code{font-family:'SF Mono',ui-monospace,Menlo,monospace;}

/* ---- task header + status pill ---- */
.task-head{margin:2px 0 16px;}
.task-crumb{font-size:.68rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase;
  color:var(--faint); display:flex; align-items:center; gap:6px;}
.task-titlebar{display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-top:6px;}
.task-title{font-size:1.55rem; font-weight:680; letter-spacing:-.032em; color:var(--ink); line-height:1.1;}
.pill{font-size:.72rem; font-weight:550; padding:3px 10px 3px 8px; border-radius:999px;
  letter-spacing:-.005em; white-space:nowrap; display:inline-flex; align-items:center; gap:5px;
  border:1px solid transparent;}
.pill .dot{width:7px; height:7px; border-radius:999px; flex:0 0 auto;}
.pill.done{background:var(--green-soft); color:var(--green-ink); border-color:#cfe8da;}
.pill.done .dot{background:var(--green);}
.pill.fail{background:var(--red-soft); color:var(--red-ink); border-color:#f0d2d4;}
.pill.fail .dot{background:var(--red);}
.pill.wip{background:var(--amber-soft); color:var(--amber-ink); border-color:#ecdcb4;}
.pill.wip .dot{background:var(--amber);}
.pill.new{background:var(--panel-2); color:var(--muted); border-color:var(--line);}
.pill.new .dot{background:var(--faint);}
/* content section headers inside the cards */
.sec{font-size:.68rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--faint);
  margin:0 0 8px; display:flex; align-items:center; gap:6px;}
.sec .icon{width:14px; height:14px; color:var(--faint);}

/* ---- level-cleared moment ---- */
.cleared{background:var(--green-soft); border:1px solid #cfe8da; border-radius:12px;
  padding:15px 17px; margin:14px 0 10px;}
.cleared-badge{font-size:1.05rem; font-weight:650; letter-spacing:-.02em; color:var(--green-ink);
  display:flex; align-items:center; gap:7px;}
.cleared-badge .icon{width:17px; height:17px; color:var(--green);}
.cleared-meta{color:var(--green-ink); opacity:.85; font-size:.82rem; font-weight:500; margin-top:3px;}

/* ---- check result lines ---- */
.chk{display:flex; align-items:flex-start; gap:8px; margin:4px 0; font-size:.9rem; color:var(--ink);}
.chk .dot{width:8px; height:8px; border-radius:999px; margin-top:6px; flex:0 0 auto;}
.d-done{background:var(--green);} .d-fail{background:var(--red);}
.d-wip{background:var(--amber);} .d-new{background:var(--faint);}
</style>
"""

# Consistent line icons (Linear/Bento): thin-stroke SVG, inherit currentColor.
def _ic(paths: str) -> str:
    return f'<svg class="icon" viewBox="0 0 24 24">{paths}</svg>'

_ICON = {
    "spark": _ic('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2 2M16 16l2 2M18 6l-2 2M8 16l-2 2"/>'),
    "home": _ic('<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>'),
    "book": _ic('<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 19a2 2 0 0 1 2-2h12"/>'),
    "reading": _ic('<path d="M12 6c-2-1.5-5-1.5-7 0v12c2-1.5 5-1.5 7 0 2-1.5 5-1.5 7 0V6c-2-1.5-5-1.5-7 0z"/><path d="M12 6v12"/>'),
    "code": _ic('<path d="M8 9l-3 3 3 3M16 9l3 3-3 3"/>'),
    "check": _ic('<path d="M20 6L9 17l-5-5"/>'),
    "arrow": _ic('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "target": _ic('<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>'),
    "lock": _ic('<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'),
}


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

    st.sidebar.markdown(f'<div class="brand">{_ICON["spark"]} Learn by doing</div>',
                        unsafe_allow_html=True)
    if not tasks:
        st.sidebar.info("No tasks found yet.")
        st.title("No tasks found")
        st.write("Add a task under `projects/datamart-intelligence-platform/tasks/`.")
        return

    done = sum(1 for s, t in tasks if progress.get(s, {}).get(t, {}).get("status") == "pass")

    if st.sidebar.button("Home", icon=":material/home:", use_container_width=True,
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
            badge = ":material/check_circle:"        # every level cleared
        elif sprint == on_sprint:
            badge = ":material/adjust:"              # the sprint you're on
        elif c_done:
            badge = ":material/pending:"             # partway in — momentum
        elif sprint_locked:
            badge = ":material/lock:"                # finish the levels ahead first
        else:
            badge = ":material/radio_button_unchecked:"  # not started
        header = f"{_sprint_label(sprint)} · {c_done}/{c_total}"
        # Open the sprint you're on, or one you've navigated into.
        expanded = sprint in (on_sprint, sel_sprint_now)
        with st.sidebar.expander(header, expanded=expanded, icon=badge):
            for task in sprint_tasks:
                locked = _is_locked(tasks, progress, sprint, task)
                micon = ":material/lock:" if locked \
                    else _STATE_MICON[_task_state(sprint, task, progress)]
                here = "  ‹" if (sprint, task) == nxt else ""
                if st.button(f"{task}{here}", key=f"nav-{sprint}-{task}", icon=micon,
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
        label = "Start learning" if done == 0 else f"Continue at level {level}"
        st.caption(f"Next up: **{_sprint_label(nxt[0])} · {nxt[1]}**")
        if st.button(label, type="primary", use_container_width=True,
                     icon=":material/play_arrow:"):
            st.session_state.sel = nxt
            st.rerun()
    else:
        st.success("You've passed every task. Nice work.", icon=":material/celebration:")

    if not _stack_up():
        st.warning("The data stack looks **down**. Real-infra tasks need it — start with "
                   "`./platform.sh up` (or `docker compose up -d`).")

    if GLOSSARY.is_file():
        with st.expander("Glossary — data engineering terms", icon=":material/book_2:"):
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
            st.markdown(f'<div class="sec">{_ICON["lock"]} Locked</div>', unsafe_allow_html=True)
            st.write("Finish the levels ahead of this one first — the path is meant "
                     "to be walked in order, so each level builds on the last.")
            if nxt and st.button(f"Go to level {_level_of(tasks, *nxt)} · {nxt[1]}",
                                 type="primary", icon=":material/arrow_forward:"):
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
            st.markdown(f'<div class="sec">{_ICON["book"]} Lesson</div>', unsafe_allow_html=True)
            lesson_file = spec.task_dir / "lesson.md"
            if lesson_file.is_file():
                st.markdown(lesson_file.read_text())
            elif spec.scaffold:
                st.markdown("Read the scaffold, then write your solution.")
                st.code((spec.task_dir / spec.scaffold).read_text(), language=lang)
            else:
                st.info("No lesson text for this task yet.")

            reading_file = spec.task_dir / "reading.md"
            if reading_file.is_file():
                with st.expander("Reading — the concept behind this level",
                                 icon=":material/auto_stories:"):
                    st.markdown(reading_file.read_text())

            intro = _load_sprint_intro(sprint)
            if intro:
                with st.expander(f"About {_sprint_label(sprint)}", icon=":material/info:"):
                    st.markdown(intro)

            preview = _preview_tables(sprint, spec)
            if preview and _stack_up():
                with st.expander("Peek at the data", icon=":material/table:"):
                    for i, table in enumerate(preview):
                        st.caption(f"`{table}`")
                        records = _safe_preview(table, seed=(i == 0))
                        if records:
                            st.dataframe(records, use_container_width=True, hide_index=True)
                        else:
                            st.caption("_(empty or unavailable)_")

    with col_work:
        with st.container(border=True):
            st.markdown(f'<div class="sec">{_ICON["code"]} Your work</div>', unsafe_allow_html=True)
            if not submission.exists():
                st.info("You haven't started this task yet.")
                if spec.scaffold and st.button("Start this task", type="primary",
                                               use_container_width=True,
                                               icon=":material/play_arrow:"):
                    start(sprint, task, REPO_ROOT, overwrite=False)
                    st.rerun()
            else:
                current = submission.read_text()
                edited = st.text_area("Edit your submission", value=current, height=280,
                                      key=f"editor-{sprint}-{task}",
                                      label_visibility="collapsed")

                # One hero action. Checking always saves first — no separate step.
                if st.button("Check my work", type="primary", use_container_width=True,
                             icon=":material/check:"):
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
                    if cols[i].button("Run", use_container_width=True, icon=":material/play_arrow:",
                                      help="Run this query against the warehouse"):
                        submission.write_text(edited)
                        st.session_state[_res_key(sprint, task)] = None
                        _run_playground(edited)
                    i += 1
                if cols[i].button("Save", use_container_width=True, icon=":material/save:"):
                    submission.write_text(edited)
                    st.toast("Saved.")
                i += 1
                if spec.scaffold and cols[i].button("Reset", use_container_width=True,
                                                    icon=":material/restart_alt:"):
                    start(sprint, task, REPO_ROOT, overwrite=True)
                    st.session_state.pop(_res_key(sprint, task), None)
                    st.rerun()

            if spec.solution:
                solution_file = spec.task_dir / spec.solution
                if solution_file.is_file():
                    with st.expander("Stuck? Reveal a worked solution",
                                     icon=":material/lightbulb:"):
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
    _dot_cls = {"pass": "done", "fail": "fail", "error": "wip"}
    for check in result.checks:
        cls = _dot_cls.get(check.status.value, "new")
        hint = "" if check.status is Status.PASS else f" — {check.hint}"
        st.markdown(
            f'<div class="chk"><span class="dot d-{cls}"></span>'
            f'<span><b>{check.name}</b>{hint}</span></div>',
            unsafe_allow_html=True,
        )

    if result.status is Status.PASS:
        _render_cleared(sprint, task, tasks, celebrate)
        if result.proof_dir is not None:
            rel = result.proof_dir.relative_to(REPO_ROOT)
            st.info(f"Portfolio artifact written to `{rel}` — commit it to your "
                    f"GitHub to show what you built.", icon=":material/workspace_premium:")
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
        f'<div class="cleared-badge">{_ICON["check"]} Level cleared</div>'
        f'<div class="cleared-meta">{done} of {len(tasks)} done{onto}</div>'
        "</div>",
        unsafe_allow_html=True,
    )
    if nxt:
        if st.button(f"Next level — {nxt[1]}", type="primary", icon=":material/arrow_forward:",
                     use_container_width=True, key=f"next-{sprint}-{task}"):
            st.session_state.pop(_res_key(sprint, task), None)
            st.session_state.sel = nxt
            st.rerun()
    else:
        st.success("You've cleared the whole path — every level passed. Incredible.",
                   icon=":material/military_tech:")


_STATUS_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️"}


if __name__ == "__main__":
    main()
