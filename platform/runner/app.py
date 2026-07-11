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

import os
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

_REAL_INFRA_CHECKS = {"sql_assert", "dbt_test", "airflow"}
# ============================================================================
# THE CURRICULUM — single source of truth.
# Five phases (Foundations → Scaling → Real-time → Production → Capstone), each
# with a phase intro; every sprint carries a Focus, targeted Skills, and a
# sub-intro. Sprint ORDER here defines the learning order and the global
# "Sprint N" numbering; it must match grader.core._SPRINT_ORDER (a test guards
# this). `stage` is the short label used in the lifecycle journey stepper.
# ============================================================================
_CURRICULUM = [
    {
        "title": "Phase 1 · Foundations",
        "intro": "The bedrock of every pipeline: query data with SQL, land it "
                 "reliably in the warehouse, model it with dbt, and schedule it "
                 "with Airflow. Finish here and you can build and run a batch "
                 "pipeline end to end.",
        "sprints": [
            {"key": "sql-fundamentals", "name": "SQL Foundations", "stage": "Query",
             "focus": "Read data confidently with SQL — the language every layer builds on.",
             "skills": ["SELECT & WHERE", "JOIN", "GROUP BY", "HAVING", "CASE", "window functions"],
             "intro": "Start where every pipeline starts: pulling the exact rows you "
                      "need. You'll filter, join, aggregate, and rank real e-commerce "
                      "data until querying is second nature."},
            {"key": "ingestion", "name": "Cloud Data Ingestion", "stage": "Ingest",
             "focus": "Land raw source data into the warehouse — cleanly and repeatably.",
             "skills": ["INSERT…SELECT", "dedupe", "idempotent upserts", "incremental loads", "CDC", "quarantine"],
             "intro": "Get data in without making a mess. You'll load feeds "
                      "idempotently, dedupe by key, apply change-data-capture, and "
                      "quarantine anything that fails validation."},
            {"key": "sprint-2-dbt", "name": "Modern Transformation", "stage": "Transform",
             "focus": "Turn raw tables into trustworthy analytics models with dbt.",
             "skills": ["dbt models", "sources & refs", "star schema", "aggregations", "dbt tests"],
             "intro": "Model the business, not just the data. You'll build dbt models "
                      "over your raw sources, shape a star schema, and let dbt tests "
                      "guard the numbers."},
            {"key": "sprint-3-airflow", "name": "Workflow Orchestration", "stage": "Orchestrate",
             "focus": "Schedule and chain the pipeline into reliable, repeatable runs.",
             "skills": ["Airflow DAGs", "PythonOperator", "task dependencies", "schedules", "retries"],
             "intro": "Make it run on its own. You'll author Airflow DAGs, wire task "
                      "dependencies, set schedules, and add retries so a transient blip "
                      "doesn't page you."},
        ],
    },
    {
        "title": "Phase 2 · Scaling",
        "intro": "Grow past a single machine and a single tool: distributed processing "
                 "with Spark, the cloud lakehouse and its cost model, hybrid job "
                 "orchestration, and the data-quality and serving layers that make "
                 "output trustworthy and usable.",
        "sprints": [
            {"key": "sprint-4-spark", "name": "Big Data Processing", "stage": "Process",
             "focus": "Process data that won't fit on one machine, with Spark.",
             "skills": ["Spark DataFrames", "groupBy/agg", "joins", "window functions", "partition & cache"],
             "intro": "Scale out. You'll rewrite familiar transforms as distributed "
                      "Spark jobs — aggregations, joins, ranking, and partition-aware "
                      "performance."},
            {"key": "sprint-cloud", "name": "Cloud & Lakehouse", "stage": "Cloud",
             "focus": "Work the modern cloud lakehouse and its cost model.",
             "skills": ["scan cost / FinOps", "partition pruning", "medallion", "Delta MERGE", "time travel"],
             "intro": "Think like the cloud bill. You'll price queries by bytes "
                      "scanned, prune partitions, refine bronze into silver, upsert "
                      "with Delta MERGE, and read a table as of a past version."},
            {"key": "sprint-5-hybrid-cloud", "name": "Hybrid Pipelines", "stage": "Hybrid",
             "focus": "Drive remote/cloud jobs and stitch systems together via APIs.",
             "skills": ["job submit/poll", "terminal states", "timeouts", "success gating", "failure handling"],
             "intro": "Orchestrate across boundaries. You'll submit jobs to a remote "
                      "service, poll to terminal states with timeouts, gate downstream "
                      "work on success, and handle failures."},
            {"key": "data-quality", "name": "Data Quality & Testing", "stage": "Validate",
             "focus": "Prove the data is right — catch defects before they reach users.",
             "skills": ["data tests", "not-null / unique", "orphan / FK checks", "range checks", "valid sets"],
             "intro": "Trust, but verify. You'll write tests that return the offending "
                      "rows — duplicate emails, null keys, orphaned orders, impossible "
                      "dates — and only pass when the data is clean."},
            {"key": "serving", "name": "Serving & BI", "stage": "Serve",
             "focus": "Shape analytics-ready marts and KPIs for the business.",
             "skills": ["serving marts", "headline KPIs", "running totals", "ranking", "customer-360"],
             "intro": "Deliver the numbers people actually read. You'll build KPI "
                      "queries, running totals, category rankings, and a wide "
                      "customer-360 serving table."},
        ],
    },
    {
        "title": "Phase 3 · Real-time",
        "intro": "Leave batch behind. Work with unbounded event streams — producing "
                 "and consuming, windowed and stateful aggregation, and the live "
                 "metrics a real-time dashboard renders.",
        "sprints": [
            {"key": "streaming", "name": "Streaming Data", "stage": "Stream",
             "focus": "Move from batch to event streams with Kafka / Redpanda.",
             "skills": ["producers & consumers", "JSON serialization", "offsets", "key partitioning", "dedupe"],
             "intro": "Data in motion. You'll produce and consume events, key-partition "
                      "for ordering, track offsets, and dedupe a replayed stream."},
            {"key": "sprint-8-realtime", "name": "Real-time Analytics", "stage": "Real-time",
             "focus": "Aggregate unbounded streams with time windows and state.",
             "skills": ["tumbling/sliding/session windows", "F.window", "watermarks", "windowed aggregates", "Structured Streaming"],
             "intro": "Answer questions as events arrive. You'll bucket a stream into "
                      "time windows, handle late data with watermarks, and compute "
                      "windowed revenue, counts, and distinct users."},
            {"key": "sprint-9-dashboard", "name": "Unified Dashboards", "stage": "Dashboard",
             "focus": "Compute the metrics a real-time dashboard renders.",
             "skills": ["moving averages", "pct change", "normalization", "top-N", "threshold bands"],
             "intro": "Turn rows into signals. You'll compute moving averages, "
                      "percentage changes, normalized series, top categories, and "
                      "health thresholds for the dashboard."},
        ],
    },
    {
        "title": "Phase 4 · Production",
        "intro": "The difference between 'it works on my machine' and 'it runs the "
                 "business': security and governance, warehouse architecture, "
                 "reliability engineering, on-call incident response, debugging, safe "
                 "migrations, and the advanced algorithms expected of a senior.",
        "sprints": [
            {"key": "security", "name": "Data Security", "stage": "Secure",
             "focus": "Lock down who can see and do what in the warehouse.",
             "skills": ["GRANT / REVOKE", "column-level grants", "PII masking", "read-only roles", "row-level security"],
             "intro": "Least privilege by default. You'll grant scoped access, mask "
                      "PII, create read-only analysts, and enforce row-level security "
                      "policies."},
            {"key": "architecture", "name": "Architecture & Modeling", "stage": "Design",
             "focus": "Design the warehouse: dimensions, facts, and history.",
             "skills": ["dimension tables", "fact grain", "SCD Type 2", "daily snapshots", "surrogate keys"],
             "intro": "Model for the long run. You'll build conformed dimensions and "
                      "facts, track history with slowly-changing dimensions, and "
                      "capture point-in-time snapshots."},
            {"key": "sprint-10-production", "name": "Production Engineering", "stage": "Production",
             "focus": "Make pipelines reliable, observable, and self-healing.",
             "skills": ["retry / backoff", "circuit breakers", "error rate & SLAs", "freshness", "idempotent dedupe", "partition paths"],
             "intro": "Ship things that stay up. You'll compute error rates and SLAs, "
                      "add exponential backoff and circuit breakers, check freshness, "
                      "and build idempotent, partition-aware writes."},
            {"key": "sprint-oncall", "name": "On-Call & Incidents", "stage": "On-Call",
             "focus": "Respond when the pager goes off.",
             "skills": ["alert triage", "root-cause analysis", "backfill windows", "recovery verification"],
             "intro": "It's 3am and a table is stale. You'll triage alerts by severity, "
                      "trace the first failure, compute the exact backfill window, and "
                      "verify recovery."},
            {"key": "sprint-debug", "name": "Debugging Pipelines", "stage": "Debug",
             "focus": "Find and fix real defects in existing code.",
             "skills": ["reading buggy code", "dedup logic", "rate / percentage math", "revenue filters"],
             "intro": "Not everything is greenfield. You'll be handed working-but-wrong "
                      "functions and hunt the planted bug — a bad dedupe, a missing "
                      "×100, an unfiltered sum."},
            {"key": "sprint-migration", "name": "Schema Migration", "stage": "Migrate",
             "focus": "Evolve schemas without losing or corrupting data.",
             "skills": ["column rename / remap", "backfilling defaults", "row-count reconciliation"],
             "intro": "Change the shape safely. You'll remap columns, backfill new "
                      "fields without clobbering existing values, and reconcile row "
                      "counts across a migration."},
            {"key": "sprint-advanced", "name": "Advanced Challenges", "stage": "Advanced",
             "focus": "Tackle the algorithms senior DEs are expected to know.",
             "skills": ["sessionization", "cohort retention", "topological sort", "blast-radius / graphs"],
             "intro": "Level up to senior. You'll sessionize events by gap, compute "
                      "cohort retention, topologically order a DAG, and trace blast "
                      "radius through a dependency graph."},
        ],
    },
    {
        "title": "Phase 5 · Capstone",
        "intro": "Bring it all together in portfolio-grade projects — a full analytics "
                 "platform, an incident response, and a stateful streaming pipeline — "
                 "the pieces you'll walk through in interviews.",
        "sprints": [
            {"key": "capstone", "name": "Capstone Projects", "stage": "Capstone",
             "focus": "Integrate everything into portfolio-grade, end-to-end projects.",
             "skills": ["end-to-end analytics", "incident response", "stateful streaming"],
             "intro": "Prove you can do the job. Three integrative capstones — a full "
                      "analytics platform, an incident response, and a stateful "
                      "streaming pipeline — the work you'll show in interviews."},
        ],
    },
]

# Flatten to the lookups the rest of the app uses (all derived from _CURRICULUM).
_SPRINT_META = {s["key"]: s for ph in _CURRICULUM for s in ph["sprints"]}
_SPRINT_LABELS = {k: m["name"] for k, m in _SPRINT_META.items()}


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

# The lifecycle journey stepper: (sprint, short stage label), in learning order.
_JOURNEY = [(k, m["stage"]) for k, m in _SPRINT_META.items()]

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
/* Dark mode. The wrapper is swapped at inject time by the theme toggle:
   Auto → `@media (prefers-color-scheme: dark)`, Dark → applied always,
   Light → a never-matching query. The palette is monochrome, so this is a
   token flip: dark surfaces, light ink, colour reserved for status. */
/*__DARK_OPEN__*/
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
  /* the primary CTA inverts: a light button with dark ink text. The `.stApp`
     prefix raises specificity so this beats the later base `color:#fff` rule —
     otherwise the label renders white on a light button (washed out). */
  .stApp [data-testid="stBaseButton-primary"],
  .stApp [data-testid="stBaseButton-primary"] *{color:#16171a!important;}
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
/*__DARK_CLOSE__*/
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
  color:var(--ink)!important; font-weight:600!important; box-shadow:inset 2px 0 0 var(--accent)!important;}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover{background:var(--line)!important;}
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

/* ---- progressive hints (the stuck-buster) — turn a FAIL into a step ---- */
.hintbox{background:var(--amber-soft); border:1px solid var(--line);
  border-left:3px solid var(--amber); border-radius:8px; padding:11px 14px; margin:8px 0;}
.hintbox .hint-lbl{font-size:.64rem; font-weight:650; letter-spacing:.06em;
  text-transform:uppercase; color:var(--amber-ink); display:flex; align-items:center;
  gap:6px; margin-bottom:4px;}
.hintbox .hint-lbl .icon{width:14px; height:14px; color:var(--amber);}
.hintbox .hint-txt{color:var(--ink); font-size:.9rem; line-height:1.5;}
.hintbox .hint-txt code{background:var(--panel-2); border:1px solid var(--line);
  border-radius:5px; padding:1px 5px; font-size:.85em;}
/* ---- AI tutor (opt-in) — a personalized nudge, visually its own thing ---- */
.tutor-lbl{font-size:.64rem; font-weight:650; letter-spacing:.06em;
  text-transform:uppercase; color:var(--faint); display:flex; align-items:center;
  gap:6px; margin-bottom:2px;}
.tutor-lbl .icon{width:14px; height:14px; color:var(--accent-h);}

/* ---- modern nav (Learnify-inspired, monochrome) ---- */
[data-testid="stSidebar"] .navcap{font-size:.6rem; font-weight:650; letter-spacing:.09em;
  text-transform:uppercase; color:var(--faint); margin:16px 8px 5px;}
/* bottom progress card, like Learnify's plan card */
[data-testid="stSidebar"] .sidecard{background:var(--panel-2); border:1px solid var(--line);
  border-radius:12px; padding:12px 13px; margin:8px 4px 6px;}
[data-testid="stSidebar"] .sidecard .sc-top{display:flex; justify-content:space-between;
  align-items:baseline; margin-bottom:8px;}
[data-testid="stSidebar"] .sidecard .sc-lbl{font-size:.72rem; font-weight:600; color:var(--ink);}
[data-testid="stSidebar"] .sidecard .sc-pct{font-size:.68rem; color:var(--faint); font-weight:600;}
[data-testid="stSidebar"] .sidecard .sc-bar{height:5px; background:var(--line-2); border-radius:999px; overflow:hidden;}
[data-testid="stSidebar"] .sidecard .sc-bar span{display:block; height:100%; background:var(--green); border-radius:999px;}
/* a right-aligned count chip baked into a sidebar button label */
[data-testid="stSidebar"] .stButton>button p{display:flex; align-items:center; width:100%;}

/* ---- sprint page (main area) task cards ---- */
.sprint-head{background:var(--panel); border:1px solid var(--line); border-radius:16px;
  padding:20px 22px; margin-bottom:16px; box-shadow:var(--sh);}
.sprint-role{font-size:.62rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--faint);}
.sprint-name{font-size:1.5rem; font-weight:680; letter-spacing:-.025em; color:var(--ink); margin-top:3px;}
.sprint-meta{color:var(--muted); font-size:.85rem; margin-top:6px;}
.sprint-bar{height:6px; background:var(--line-2); border-radius:999px; margin-top:14px; overflow:hidden;}
.sprint-bar span{display:block; height:100%; background:var(--green); border-radius:999px;}
.tcard-h{display:flex; align-items:center; gap:9px; margin-bottom:2px;}
.tcard-h .dot{width:9px; height:9px; border-radius:999px; flex:0 0 auto;}
.tcard-lvl{font-size:.64rem; font-weight:600; letter-spacing:.05em; text-transform:uppercase; color:var(--faint);}
.tcard-title{font-size:.98rem; font-weight:620; color:var(--ink); letter-spacing:-.01em; margin:1px 0 2px;}
.tcard-sub{font-size:.8rem; color:var(--muted); line-height:1.4; min-height:2.2em;}

/* ===== Learnify-style custom sidebar (HTML nav, query-param links) ===== */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] a{text-decoration:none;}
.lf-brand{display:flex; align-items:center; gap:10px; padding:4px 4px 12px;}
.lf-logo{width:30px; height:30px; border-radius:9px; background:var(--accent);
  display:flex; align-items:center; justify-content:center; flex:0 0 auto;}
.lf-logo .icon{width:16px; height:16px; color:var(--panel);}
.lf-brandname{font-weight:680; font-size:1.02rem; letter-spacing:-.02em; color:var(--ink);}
.lf-nav{display:flex; align-items:center; gap:11px; padding:9px 11px; margin:2px 0; border-radius:9px;
  color:var(--muted)!important; font-size:.9rem; font-weight:500; letter-spacing:-.01em;
  cursor:pointer; transition:background .12s,color .12s;}
.lf-nav:hover{background:var(--panel-2); color:var(--ink)!important;}
.lf-nav.active{background:var(--accent-soft); color:var(--ink)!important; font-weight:600;}
.lf-nav .icon{width:18px; height:18px; color:currentColor; flex:0 0 auto;}
.lf-nav .lf-caret{margin-left:auto; width:15px; height:15px;}
.lf-nav.open .lf-caret{transform:rotate(180deg);}
.lf-sub{margin:1px 0 6px 21px; padding-left:13px; border-left:1.5px solid var(--line);
  display:flex; flex-direction:column; gap:2px;}
.lf-subitem{display:flex; align-items:center; padding:7px 10px; border-radius:8px;
  color:var(--muted)!important; font-size:.85rem; font-weight:500; letter-spacing:-.01em; cursor:pointer;}
.lf-subitem:hover{background:var(--panel-2); color:var(--ink)!important;}
.lf-subitem.active{background:var(--panel); box-shadow:var(--sh); color:var(--ink)!important; font-weight:600;}
.lf-badge{margin-left:auto; font-size:.67rem; font-weight:600; color:var(--faint);
  background:var(--panel-2); border:1px solid var(--line); border-radius:999px;
  padding:1px 8px; min-width:20px; text-align:center;}
.lf-subitem.active .lf-badge{background:var(--accent); color:var(--panel); border-color:var(--accent);}
.lf-cap{font-size:.6rem; font-weight:650; letter-spacing:.09em; text-transform:uppercase;
  color:var(--faint); margin:15px 10px 5px;}
/* progress card (Learnify's plan card) */
.lf-card{background:var(--panel-2); border:1px solid var(--line); border-radius:13px;
  padding:13px 14px; margin:8px 2px 4px;}
.lf-card-top{display:flex; align-items:center; gap:9px; margin-bottom:9px;}
.lf-card-ic{width:28px; height:28px; border-radius:8px; background:var(--accent-soft);
  display:flex; align-items:center; justify-content:center; flex:0 0 auto;}
.lf-card-ic .icon{width:15px; height:15px; color:var(--accent);}
.lf-card-t{font-size:.78rem; font-weight:650; color:var(--ink); line-height:1.15;}
.lf-card-s{font-size:.67rem; color:var(--faint); margin-top:1px;}
.lf-card-bar{height:6px; background:var(--line-2); border-radius:999px; overflow:hidden;}
.lf-card-bar span{display:block; height:100%; background:var(--green); border-radius:999px;}
/* profile footer */
.lf-profile{display:flex; align-items:center; gap:10px; padding:11px 6px 2px;}
.lf-avatar{width:34px; height:34px; border-radius:50%; background:var(--accent); color:var(--panel);
  display:flex; align-items:center; justify-content:center; font-weight:650; font-size:.82rem;
  flex:0 0 auto; position:relative;}
.lf-dot{position:absolute; right:-1px; bottom:-1px; width:10px; height:10px; border-radius:50%;
  background:var(--green); border:2px solid var(--panel);}
.lf-pname{font-size:.82rem; font-weight:600; color:var(--ink); line-height:1.15;}
.lf-psub{font-size:.69rem; color:var(--faint);}

/* curriculum sprint-card grid (anchor cards) */
.sc-grid{display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:14px;}
[data-testid="stMarkdownContainer"] a.scard, a.scard *{text-decoration:none!important;}
.scard{display:block; background:var(--panel); border:1px solid var(--line); border-radius:14px;
  padding:16px 17px; box-shadow:var(--sh); transition:border-color .12s, transform .06s;}
.scard:hover{border-color:var(--accent-h); transform:translateY(-1px);}
.scard.locked{opacity:.55;}
.scard-role{display:flex; align-items:center; gap:7px; font-size:.6rem; font-weight:600;
  letter-spacing:.07em; text-transform:uppercase; color:var(--faint);}
.scard-role .dot{width:7px; height:7px; border-radius:999px;}
.scard-name{font-size:1.05rem; font-weight:650; color:var(--ink)!important; letter-spacing:-.02em; margin:4px 0 2px;}
.scard-meta{font-size:.75rem; color:var(--muted); margin-bottom:10px;}
.scard-bar{height:5px; background:var(--line-2); border-radius:999px; overflow:hidden;}
.scard-bar span{display:block; height:100%; background:var(--green); border-radius:999px;}
.phase-head{display:flex; align-items:baseline; gap:10px; margin:26px 2px 12px;}
.phase-head:first-of-type{margin-top:6px;}
.phase-title{font-size:.95rem; font-weight:680; letter-spacing:-.02em; color:var(--ink);}
.phase-count{font-size:.72rem; color:var(--faint); font-weight:500;}
.phase-rule{flex:1; height:1px; background:var(--line);}
.phase-intro{color:var(--muted); font-size:.85rem; line-height:1.55; max-width:780px; margin:-4px 2px 15px;}
/* rich sprint cards: focus line + skill chips */
.scard-focus{font-size:.81rem; color:var(--muted); line-height:1.45; margin:3px 0 9px; min-height:2.3em;}
.scard-chips{display:flex; flex-wrap:wrap; gap:5px; margin-bottom:11px;}
.chip{font-size:.66rem; font-weight:500; color:var(--muted); background:var(--panel-2);
  border:1px solid var(--line); border-radius:6px; padding:2px 7px; white-space:nowrap;}
.scard.locked .chip{opacity:.7;}
/* sprint-page header: focus, sub-intro, skills */
.sprint-focus{font-size:.96rem; color:var(--ink); font-weight:550; margin:9px 0 7px; letter-spacing:-.01em;}
.sprint-intro{font-size:.88rem; color:var(--muted); line-height:1.55; max-width:680px; margin-bottom:13px;}
.sprint-skills{display:flex; align-items:center; gap:9px; flex-wrap:wrap; margin-bottom:15px;}
.sprint-skills-lbl{font-size:.6rem; font-weight:650; letter-spacing:.08em; text-transform:uppercase; color:var(--faint);}
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
    "bulb": _ic('<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.6.6 1 1.4 1 2.5h6c0-1.1.4-1.9 1-2.5A6 6 0 0 0 12 3z"/>'),
    "tutor": _ic('<path d="M12 4 2 9l10 5 10-5-10-5z"/><path d="M6 11v5c0 1 3 2.5 6 2.5s6-1.5 6-2.5v-5"/>'),
    "gear": _ic('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'),
    "caret": _ic('<path d="M6 9l6 6 6-6"/>'),
    "code": _ic('<path d="M8 9l-3 3 3 3M16 9l3 3-3 3"/>'),
    "check": _ic('<path d="M20 6L9 17l-5-5"/>'),
    "arrow": _ic('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "target": _ic('<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>'),
    "lock": _ic('<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'),
}


_DARK_WRAP = {
    "auto": ("@media (prefers-color-scheme: dark){", "}"),
    "dark": ("", ""),               # dark rules apply unconditionally
    "light": ("@media not all{", "}"),  # a query that never matches → pure light
}


def _inject_css(theme: str = "auto") -> None:
    open_, close_ = _DARK_WRAP.get(theme, _DARK_WRAP["auto"])
    css = _CSS.replace("/*__DARK_OPEN__*/", open_).replace("/*__DARK_CLOSE__*/", close_)
    st.markdown(css, unsafe_allow_html=True)


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


# ---------- navigation ----------
def _save_theme() -> None:
    """Persist the theme choice to the state volume so it survives a restart."""
    from grader import settings
    settings.save(REPO_ROOT, {"theme": st.session_state.theme_choice}, settings.PREFS_FILENAME)


def _goto(v: str, s: str | None = None, t: str | None = None, f: str | None = None) -> None:
    """Navigate by rewriting the URL query params, then rerun."""
    st.query_params.clear()
    st.query_params["v"] = v
    if s:
        st.query_params["s"] = s
    if t:
        st.query_params["t"] = t
    if f:
        st.query_params["f"] = f
    st.rerun()


def _nav(v: str, icon: str, label: str, active: bool) -> str:
    cls = "lf-nav active" if active else "lf-nav"
    return (f'<a class="{cls}" href="?v={v}" target="_self">'
            f'{_ICON[icon]}<span>{label}</span></a>')


def _sidebar_html(tasks, progress, view, f, done, inprog, total) -> str:
    """The Learnify-style sidebar: brand, icon nav rows, a Curriculum group with
    connector-line sub-items + count pills, a progress card, and a profile
    footer. Nav is plain <a> query-param links — no Streamlit widget chrome."""
    pct = round(done / total * 100) if total else 0
    cur = view == "curriculum"

    def sub(fname, label, count):
        cls = "lf-subitem active" if (cur and f == fname) else "lf-subitem"
        return (f'<a class="{cls}" href="?v=curriculum&amp;f={fname}" target="_self">'
                f'<span>{label}</span><span class="lf-badge">{count}</span></a>')

    nxt = next_task(REPO_ROOT)
    psub = (f'Level {_level_of(tasks, *nxt)} · {_sprint_label(nxt[0])}'
            if nxt else 'Every level cleared')
    return (
        f'<div class="lf-brand"><span class="lf-logo">{_ICON["spark"]}</span>'
        f'<span class="lf-brandname">Learn by doing</span></div>'
        + _nav("home", "home", "Home", view == "home")
        + f'<a class="lf-nav{" open" if cur else ""}" href="?v=curriculum&amp;f=all" '
          f'target="_self">{_ICON["book"]}<span>Curriculum</span>'
          f'<span class="lf-caret">{_ICON["caret"]}</span></a>'
        + '<div class="lf-sub">'
        + sub("progress", "In progress", inprog)
        + sub("done", "Completed", done)
        + sub("all", "All levels", total)
        + '</div>'
        + '<div class="lf-cap">More</div>'
        + _nav("glossary", "reading", "Glossary", view == "glossary")
        + _nav("settings", "gear", "Settings", view == "settings")
        + f'<div class="lf-card"><div class="lf-card-top">'
          f'<span class="lf-card-ic">{_ICON["spark"]}</span>'
          f'<div><div class="lf-card-t">Your progress</div>'
          f'<div class="lf-card-s">{done} of {total} levels cleared</div></div></div>'
          f'<div class="lf-card-bar"><span style="width:{pct}%"></span></div></div>'
        + f'<div class="lf-profile"><span class="lf-avatar">L<span class="lf-dot"></span></span>'
          f'<div><div class="lf-pname">Learner</div><div class="lf-psub">{psub}</div></div></div>'
    )


# ---------- main ----------
def main() -> None:
    st.set_page_config(page_title="Learn Data Engineering", page_icon="🧪", layout="wide")
    # Seed the theme from the persisted pref before first paint (no light→dark flash).
    if "theme_choice" not in st.session_state:
        from grader import settings
        st.session_state.theme_choice = \
            settings.load(REPO_ROOT, settings.PREFS_FILENAME).get("theme", "Auto")
    _inject_css(st.session_state.theme_choice.lower())

    tasks = discover_tasks(REPO_ROOT)
    progress = load_progress(REPO_ROOT)
    if not tasks:
        st.sidebar.info("No tasks found yet.")
        st.title("No tasks found")
        st.write("Add a task under `projects/datamart-intelligence-platform/tasks/`.")
        return

    view = st.query_params.get("v", "home")
    f = st.query_params.get("f", "all")
    done = sum(1 for s, t in tasks if progress.get(s, {}).get(t, {}).get("status") == "pass")
    total = len(tasks)
    inprog = sum(1 for s, t in tasks
                 if progress.get(s, {}).get(t, {}).get("status") != "pass"
                 and not _is_locked(tasks, progress, s, t))

    st.sidebar.markdown(_sidebar_html(tasks, progress, view, f, done, inprog, total),
                        unsafe_allow_html=True)

    # ---- route on the URL ----
    if view == "settings":
        _render_settings()
    elif view == "glossary":
        _render_glossary()
    elif view == "curriculum":
        _render_curriculum(tasks, progress, f)
    elif view == "sprint" and st.query_params.get("s"):
        _render_sprint(st.query_params.get("s"), tasks, progress)
    elif view == "task" and st.query_params.get("s") and st.query_params.get("t"):
        _render_task(st.query_params.get("s"), st.query_params.get("t"), progress, tasks)
    else:
        _render_home(tasks, progress, done)


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
            _goto("task", s=nxt[0], t=nxt[1])
    else:
        st.success("You've passed every task. Nice work.", icon=":material/celebration:")

    if not _stack_up():
        st.warning("The data stack looks **down**. Real-infra tasks need it — start with "
                   "`./platform.sh up` (or `docker compose up -d`).")


def _render_sprint(sprint, tasks, progress) -> None:
    """A sprint's levels as cards in the main area — the modern nav's detail view.

    Replaces the old sidebar wall-of-tasks: pick a sprint in the rail, its levels
    show here as scannable cards you open from.
    """
    sprint_tasks = [t for s, t in tasks if s == sprint]
    if not sprint_tasks:
        st.info("No levels in this sprint yet.")
        return
    c_done = sum(1 for t in sprint_tasks
                 if progress.get(sprint, {}).get(t, {}).get("status") == "pass")
    total = len(sprint_tasks)
    pct = round(c_done / total * 100) if total else 0
    meta = _SPRINT_META.get(sprint, {})
    order = [s for s, _ in _grouped_by_sprint(tasks)]
    num = order.index(sprint) + 1 if sprint in order else None
    stage = meta.get("stage", "")
    tag = (f"Sprint {num}" if num else "Sprint") + (f" · {stage}" if stage else "")
    chips = "".join(f'<span class="chip">{sk}</span>' for sk in meta.get("skills", []))
    st.markdown(
        f'<div class="sprint-head"><div class="sprint-role">{tag}</div>'
        f'<div class="sprint-name">{_sprint_label(sprint)}</div>'
        + (f'<div class="sprint-focus">{meta["focus"]}</div>' if meta.get("focus") else "")
        + (f'<div class="sprint-intro">{meta["intro"]}</div>' if meta.get("intro") else "")
        + (f'<div class="sprint-skills"><span class="sprint-skills-lbl">Skills</span>'
           f'<span class="scard-chips">{chips}</span></div>' if chips else "")
        + f'<div class="sprint-meta">{c_done} of {total} levels cleared · {pct}%</div>'
          f'<div class="sprint-bar"><span style="width:{pct}%"></span></div></div>',
        unsafe_allow_html=True)

    detail = _load_sprint_intro(sprint)
    if detail:
        with st.expander("More about this sprint", icon=":material/info:"):
            st.markdown(detail)

    _dot = {"pass": "done", "fail": "fail", "error": "wip", "in-progress": "wip", "new": "new"}
    nxt = next_task(REPO_ROOT)
    cols = st.columns(2, gap="medium")
    for i, task in enumerate(sprint_tasks):
        state = _task_state(sprint, task, progress)
        locked = _is_locked(tasks, progress, sprint, task)
        level = _level_of(tasks, sprint, task)
        lvl_txt = f"Level {level}" + (" · locked" if locked else
                                      "  ·  you are here" if (sprint, task) == nxt else "")
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="tcard-h"><span class="dot d-{_dot.get(state, "new")}"></span>'
                    f'<span class="tcard-lvl">{lvl_txt}</span></div>'
                    f'<div class="tcard-title">{task}</div>', unsafe_allow_html=True)
                label = "Locked" if locked else ("Review" if state == "pass" else "Open")
                icon = ":material/lock:" if locked else (
                    ":material/replay:" if state == "pass" else ":material/arrow_forward:")
                highlight = not locked and (sprint, task) == nxt
                if st.button(label, key=f"open-{sprint}-{task}", use_container_width=True,
                             disabled=locked, icon=icon,
                             type="primary" if highlight else "secondary"):
                    _goto("task", s=sprint, t=task)


def _render_glossary() -> None:
    """The glossary as a first-class page (Learnify's 'Library' equivalent)."""
    st.markdown('<div class="hero"><div class="hero-title">Glossary</div>'
                '<div class="hero-sub">Plain-English definitions for the data-engineering '
                'terms you meet across the levels.</div></div>', unsafe_allow_html=True)
    if GLOSSARY.is_file():
        with st.container(border=True):
            st.markdown(GLOSSARY.read_text())
    else:
        st.info("No glossary found.")


def _render_curriculum(tasks, progress, f) -> None:
    """Curriculum browser: All levels → sprint cards; In progress / Completed →
    the matching level cards. Cards are query-param links, no widget chrome."""
    subtitle = {"all": "Every sprint in the path — open one to see its levels.",
                "progress": "Levels you can take on right now.",
                "done": "Levels you've already cleared."}.get(f, "")
    st.markdown(f'<div class="hero"><div class="hero-title">Curriculum</div>'
                f'<div class="hero-sub">{subtitle}</div></div>', unsafe_allow_html=True)

    if f == "all":
        on = _current_sprint(tasks, progress)
        grouped = _grouped_by_sprint(tasks)          # learning order
        tmap = dict(grouped)
        number = {s: i + 1 for i, (s, _) in enumerate(grouped)}  # global "Sprint N"

        def card(sprint):
            meta = _SPRINT_META.get(sprint, {})
            stasks = tmap[sprint]
            cdone = sum(1 for t in stasks
                        if progress.get(sprint, {}).get(t, {}).get("status") == "pass")
            ctot = len(stasks)
            pct = round(cdone / ctot * 100) if ctot else 0
            locked = _is_locked(tasks, progress, sprint, stasks[0])
            dot = "done" if cdone == ctot else ("wip" if (cdone or sprint == on) else "new")
            stage = meta.get("stage", "")
            tag = f"Sprint {number[sprint]}" + (f" · {stage}" if stage else "")
            chips = "".join(f'<span class="chip">{sk}</span>' for sk in meta.get("skills", [])[:5])
            cls = "scard locked" if locked else "scard"
            return (f'<a class="{cls}" href="?v=sprint&amp;s={sprint}" target="_self">'
                    f'<div class="scard-role"><span class="dot d-{dot}"></span>{tag}</div>'
                    f'<div class="scard-name">{_sprint_label(sprint)}</div>'
                    f'<div class="scard-focus">{meta.get("focus", "")}</div>'
                    f'<div class="scard-chips">{chips}</div>'
                    f'<div class="scard-meta">{cdone}/{ctot} levels · {pct}%</div>'
                    f'<div class="scard-bar"><span style="width:{pct}%"></span></div></a>')

        seen = set()
        for phase in _CURRICULUM:
            present = [s["key"] for s in phase["sprints"] if s["key"] in tmap]
            if not present:
                continue
            seen.update(present)
            pdone = sum(1 for s in present for t in tmap[s]
                        if progress.get(s, {}).get(t, {}).get("status") == "pass")
            ptot = sum(len(tmap[s]) for s in present)
            st.markdown(
                f'<div class="phase-head"><span class="phase-title">{phase["title"]}</span>'
                f'<span class="phase-count">{pdone}/{ptot} levels</span>'
                f'<span class="phase-rule"></span></div>'
                f'<div class="phase-intro">{phase["intro"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sc-grid">{"".join(card(s) for s in present)}</div>',
                        unsafe_allow_html=True)
        # safety net: any discovered sprint not placed in a phase still shows
        leftover = [s for s, _ in grouped if s not in seen]
        if leftover:
            st.markdown('<div class="phase-head"><span class="phase-title">More</span>'
                        '<span class="phase-rule"></span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sc-grid">{"".join(card(s) for s in leftover)}</div>',
                        unsafe_allow_html=True)
        return

    if f == "done":
        picks = [(s, t) for s, t in tasks
                 if progress.get(s, {}).get(t, {}).get("status") == "pass"]
        empty = "No cleared levels yet — start from Home."
    else:
        picks = [(s, t) for s, t in tasks
                 if progress.get(s, {}).get(t, {}).get("status") != "pass"
                 and not _is_locked(tasks, progress, s, t)]
        empty = "Nothing unlocked to do right now — clear the current level to open more."
    if not picks:
        st.info(empty)
        return
    dotmap = {"pass": "done", "fail": "fail", "error": "wip", "in-progress": "wip", "new": "new"}
    cards = []
    for s, t in picks:
        lvl = _level_of(tasks, s, t)
        dot = dotmap.get(_task_state(s, t, progress), "new")
        cards.append(
            f'<a class="scard" href="?v=task&amp;s={s}&amp;t={t}" target="_self">'
            f'<div class="scard-role"><span class="dot d-{dot}"></span>'
            f'{_sprint_label(s)} · Level {lvl}</div>'
            f'<div class="scard-name">{t}</div></a>')
    st.markdown(f'<div class="sc-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def _render_settings() -> None:
    """Admin surface: turn the AI tutor on/off and save the LLM of your choice.

    The key lives on your state volume (gitignored, owner-only) — never
    committed, never sent anywhere except the LLM calls you opt into.
    """
    from grader import settings as tsettings
    from grader.tutor import KEY_ENV, PROVIDERS, resolve_config

    st.markdown('<div class="hero"><div class="hero-title">Settings</div>'
                '<div class="hero-sub">Optional AI tutor — a personal, code-aware nudge '
                'when you fail a check. It never gives the answer, and it is off until '
                'you turn it on. Bring your own model and key; everything stays on this '
                'machine.</div></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="sec">{_ICON["home"]} Appearance</div>', unsafe_allow_html=True)
        st.segmented_control("Theme", ["Auto", "Light", "Dark"], key="theme_choice",
                             on_change=_save_theme,
                             help="Auto follows your device. Your choice is saved and "
                                  "persists across restarts.")

    cfg = resolve_config(REPO_ROOT)
    saved = tsettings.load(REPO_ROOT)
    has_saved_key = bool((saved.get("api_key") or "").strip())
    provider_keys = list(PROVIDERS)

    with st.container(border=True):
        st.markdown(f'<div class="sec">{_ICON["tutor"]} AI Tutor</div>',
                    unsafe_allow_html=True)
        enabled = st.toggle("Enable the AI tutor", value=cfg.enabled,
                            help="When off, the offline hint ladders are the whole story.")
        provider = st.selectbox(
            "Provider", provider_keys,
            index=provider_keys.index(cfg.provider) if cfg.provider in provider_keys else 0,
            format_func=lambda k: PROVIDERS[k]["label"])
        model = st.text_input("Model", value=cfg.model,
                              help=f"Default for this provider: {PROVIDERS[provider]['default_model']}")
        key_input = st.text_input(
            "API key", type="password",
            placeholder="•••••••• (saved)" if has_saved_key else f"{PROVIDERS[provider]['key_prefix']}…",
            help="Stored locally in .tutor.json on your state volume (gitignored, chmod 600). "
                 "Leave blank to keep the key you already saved.")

        c1, c2 = st.columns(2)
        if c1.button("Save", type="primary", use_container_width=True, icon=":material/save:"):
            api_key = key_input.strip() or (saved.get("api_key") or "")
            tsettings.save(REPO_ROOT, {
                "enabled": bool(enabled),
                "provider": provider,
                "model": model.strip(),
                "api_key": api_key,
            })
            st.success("Saved — persists across restarts on your state volume.")
            st.rerun()
        if c2.button("Clear key & disable", use_container_width=True,
                     icon=":material/delete:", disabled=not has_saved_key):
            tsettings.save(REPO_ROOT, {
                "enabled": False, "provider": provider,
                "model": model.strip(), "api_key": "",
            })
            st.success("Key cleared and tutor disabled.")
            st.rerun()

    now = resolve_config(REPO_ROOT)
    if now.ready:
        status = f'<span class="dot d-done"></span> Ready — {PROVIDERS[now.provider]["label"]} · {now.model}'
    elif now.enabled:
        status = '<span class="dot d-wip"></span> On, but no key yet — add one above'
    else:
        status = '<span class="dot d-new"></span> Off — offline hints only'
    st.markdown(f'<div class="chk">{status}</div>', unsafe_allow_html=True)
    if os.environ.get(KEY_ENV):
        st.caption(f"The `{KEY_ENV}` environment variable is also set and is used as a "
                   "fallback key when none is saved here.")
    st.caption("Privacy: your key and code never leave this machine except in the tutor "
               "requests you trigger. No key? The offline hint ladders cover every level.")


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
                _goto("task", s=nxt[0], t=nxt[1])
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
                    st.session_state.pop(f"tutor-{sprint}-{task}", None)  # fresh run, fresh nudge
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
        _render_result(stored, sprint, task, tasks, spec, celebrate=just)


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


def _failing_hints(spec, result) -> list[str]:
    """Author-written hints on the first failing check that carries any.

    Hints live under a check's ``hints:`` list in spec.yml and are matched to
    the check that actually failed, so a stuck learner gets a nudge about *their*
    error — not a generic one. Offline, deterministic, no dependencies.
    """
    failed = {c.name for c in result.checks if c.status is Status.FAIL}
    for chk in spec.checks:
        name = chk.get("name") or chk.get("type")
        if name in failed and chk.get("hints"):
            return [str(h) for h in chk["hints"]]
    return []


def _render_hints(spec, result, sprint, task) -> None:
    """A progressive, opt-in hint ladder shown under a failed check.

    Nothing auto-spoils: the learner asks for the first hint, then escalates one
    step at a time (nudge → concept → near-answer). The revealed count is
    persisted, so the ladder survives a power-down and never resets its progress.
    """
    hints = _failing_hints(spec, result)
    if not hints:
        return
    from grader.progress import hints_shown, reveal_hint

    shown = min(hints_shown(REPO_ROOT, sprint, task), len(hints))
    key = f"hint-{sprint}-{task}"

    if shown == 0:
        if st.button("Stuck? Show a hint", icon=":material/lightbulb:", key=key,
                     help="A nudge about your specific error — try it before the worked solution."):
            reveal_hint(REPO_ROOT, sprint, task)
            st.rerun()
        return

    for i in range(shown):
        st.markdown(
            f'<div class="hintbox"><div class="hint-lbl">{_ICON["bulb"]}'
            f'Hint {i + 1} of {len(hints)}</div>'
            f'<div class="hint-txt">{hints[i]}</div></div>',
            unsafe_allow_html=True,
        )

    if shown < len(hints):
        if st.button("Show next hint", icon=":material/lightbulb:", key=key):
            reveal_hint(REPO_ROOT, sprint, task)
            st.rerun()
    else:
        st.caption("That's every hint. Still stuck? Open the worked solution above — "
                   "then come back and rebuild it from memory.")


def _render_tutor(spec, result, sprint, task) -> None:
    """Opt-in AI tutor — a code-aware nudge layered ON TOP of the offline ladder.

    Only appears when the learner has exported LDE_TUTOR_KEY; with no key the
    offline hints are the whole story. It sends their actual code and the exact
    failure to Claude and shows one Socratic nudge — never the answer. Any
    failure (no network, bad key, package missing) degrades quietly to the
    offline hints above.
    """
    from grader.tutor import tutor_available

    if not tutor_available(REPO_ROOT):
        return
    tkey = f"tutor-{sprint}-{task}"
    if st.button("Ask the tutor", icon=":material/school:", key=f"btn-{tkey}",
                 help="A personal, code-aware nudge from your LLM — never the answer."):
        from grader.tutor import TutorRequest, TutorUnavailable, ask_tutor

        submission = REPO_ROOT / spec.submission_path
        lesson_file = spec.task_dir / "lesson.md"
        failed = [c for c in result.checks if c.status is Status.FAIL]
        req = TutorRequest(
            title=spec.title,
            lesson=lesson_file.read_text() if lesson_file.is_file() else "",
            code=submission.read_text() if submission.exists() else "",
            check_name=failed[0].name if failed else "",
            grader_hint=failed[0].hint if failed else "",
            author_hints=_failing_hints(spec, result),
        )
        try:
            with st.spinner("The tutor is reading your code…"):
                st.session_state[tkey] = ask_tutor(req, repo_root=REPO_ROOT)
        except TutorUnavailable as exc:
            st.session_state.pop(tkey, None)
            st.warning(f"The tutor isn't available right now ({exc}) — your offline "
                       "hints above still have you covered.")

    answer = st.session_state.get(tkey)
    if answer:
        with st.container(border=True):
            st.markdown(f'<div class="tutor-lbl">{_ICON["tutor"]} Tutor</div>',
                        unsafe_allow_html=True)
            st.markdown(answer)  # markdown, not raw HTML — model output stays sandboxed
            st.caption("A nudge, not the answer — the tutor won't hand you the solution.")


def _render_result(result, sprint, task, tasks, spec=None, celebrate=False) -> None:
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
        if spec is not None:
            _render_hints(spec, result, sprint, task)
            _render_tutor(spec, result, sprint, task)


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
            _goto("task", s=nxt[0], t=nxt[1])
    else:
        st.success("You've cleared the whole path — every level passed. Incredible.",
                   icon=":material/military_tech:")


_STATUS_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️"}


if __name__ == "__main__":
    main()
