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
    "sprint-2-dbt": "Sprint 2 · dbt",
    "sprint-3-airflow": "Sprint 3 · Airflow",
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


# ---------- main ----------
def main() -> None:
    st.set_page_config(page_title="Learn Data Engineering", page_icon="🧪", layout="wide")
    if "sel" not in st.session_state:
        st.session_state.sel = HOME

    tasks = discover_tasks(REPO_ROOT)
    progress = load_progress(REPO_ROOT)

    st.sidebar.title("🧪 Learn by doing")
    if not tasks:
        st.sidebar.info("No tasks found yet.")
        st.title("No tasks found")
        st.write("Add a task under `projects/datamart-intelligence-platform/tasks/`.")
        return

    done = sum(1 for s, t in tasks if progress.get(s, {}).get(t, {}).get("status") == "pass")
    st.sidebar.progress(done / len(tasks), text=f"{done}/{len(tasks)} tasks passed")

    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.session_state.sel = HOME

    current_sprint = None
    for sprint, task in tasks:
        if sprint != current_sprint:
            st.sidebar.markdown(f"**{_sprint_label(sprint)}**")
            current_sprint = sprint
        icon = _STATE_ICON[_task_state(sprint, task, progress)]
        if st.sidebar.button(f"{icon}  {task}", key=f"nav-{sprint}-{task}",
                             use_container_width=True):
            st.session_state.sel = (sprint, task)

    sel_sprint, sel_task = st.session_state.sel
    if sel_sprint == HOME[0]:
        _render_home(tasks, progress, done)
    else:
        _render_task(sel_sprint, sel_task, progress)


def _render_home(tasks, progress, done) -> None:
    st.title("🧪 Learn data engineering by doing")
    st.markdown(
        "Write real SQL, dbt, and Airflow. The platform grades your work against the "
        "**real stack** — not a simulation. Finish the capstone and you get a shareable "
        "portfolio artifact to put on your GitHub."
    )
    st.progress(done / len(tasks), text=f"{done} of {len(tasks)} tasks passed")

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

    st.title(spec.title)
    st.caption(f"{_sprint_label(sprint)} · {task}")

    intro = _load_sprint_intro(sprint)
    if intro:
        with st.expander(f"About {_sprint_label(sprint)}"):
            st.markdown(intro)

    if _needs_stack(spec) and not _stack_up():
        st.warning("The data stack looks **down**, so checks will report *could not run* "
                   "(not a wrong answer). Start it: `./platform.sh up`.")

    submission = REPO_ROOT / spec.submission_path
    lang = _language_for(spec.submission_path)
    col_lesson, col_work = st.columns([1, 1])

    with col_lesson:
        st.subheader("Lesson")
        lesson_file = spec.task_dir / "lesson.md"
        if lesson_file.is_file():
            st.markdown(lesson_file.read_text())
        elif spec.scaffold:
            st.markdown("Read the scaffold, then write your solution.")
            st.code((spec.task_dir / spec.scaffold).read_text(), language=lang)
        else:
            st.info("No lesson text for this task yet.")

    with col_work:
        st.subheader("Your work")
        if not submission.exists():
            st.info("Not started yet.")
            if spec.scaffold and st.button("▶ Start this task", type="primary"):
                start(sprint, task, REPO_ROOT, overwrite=False)
                st.rerun()
            return

        current = submission.read_text()
        edited = st.text_area("Edit your submission", value=current, height=240,
                              key=f"editor-{sprint}-{task}")
        with st.expander("Preview (syntax-highlighted)"):
            st.code(edited, language=lang)

        c1, c2, c3 = st.columns(3)
        if c1.button("💾 Save"):
            submission.write_text(edited)
            st.toast("Saved.")
        if c2.button("✅ Check my work", type="primary"):
            submission.write_text(edited)
            result = run_check(sprint, task, REPO_ROOT, make_proof=True)
            _render_result(result)
        if spec.scaffold and c3.button("↺ Reset to scaffold"):
            start(sprint, task, REPO_ROOT, overwrite=True)
            st.rerun()

    if spec.solution:
        solution_file = spec.task_dir / spec.solution
        if solution_file.is_file():
            with st.expander("😩 Stuck? Reveal a worked solution"):
                st.caption("Try it yourself first — the struggle is where the learning "
                           "happens. But a worked example beats staying stuck.")
                st.code(solution_file.read_text(), language=lang)


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
