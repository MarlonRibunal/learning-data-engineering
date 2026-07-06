"""Streamlit lesson-runner — the local web app.

Run it from the repo root:

    streamlit run platform/runner/app.py

It is a thin shell over the grader: the sidebar lists tasks and progress, the
main pane shows the lesson + an in-browser editor, and "Check my work" calls the
same ``run_check`` the CLI uses. Runs on the host so it can reach the stack; no
hosting, no login.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the `grader` package importable when run via `streamlit run`.
_PLATFORM_DIR = Path(__file__).resolve().parents[1]
if str(_PLATFORM_DIR) not in sys.path:
    sys.path.insert(0, str(_PLATFORM_DIR))

import streamlit as st  # noqa: E402

from grader import Status, run_check, start  # noqa: E402
from grader.core import default_tasks_root  # noqa: E402
from grader.progress import load as load_progress  # noqa: E402
from grader.spec import SpecError, load_spec  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]

_STATUS_ICON = {"pass": "✅", "fail": "❌", "error": "⚠️"}


def discover_tasks() -> list[tuple[str, str]]:
    """Return (sprint, task) pairs by scanning for spec.yml files."""
    root = default_tasks_root(REPO_ROOT)
    if not root.is_dir():
        return []
    found = []
    for spec_file in sorted(root.glob("*/*/spec.yml")):
        sprint = spec_file.parent.parent.name
        task = spec_file.parent.name
        found.append((sprint, task))
    return found


def main() -> None:
    st.set_page_config(page_title="Learn Data Engineering", page_icon="🧪", layout="wide")
    tasks = discover_tasks()
    progress = load_progress(REPO_ROOT)

    st.sidebar.title("🧪 Learn by doing")
    if not tasks:
        st.sidebar.info("No tasks found yet.")
        st.title("No tasks found")
        st.write("Add a task under `projects/datamart-intelligence-platform/tasks/`.")
        return

    labels = []
    for sprint, task in tasks:
        status = progress.get(sprint, {}).get(task, {}).get("status")
        labels.append(f"{_STATUS_ICON.get(status, '⬜')} {sprint} / {task}")

    choice = st.sidebar.radio("Tasks", options=range(len(tasks)),
                              format_func=lambda i: labels[i])
    sprint, task = tasks[choice]

    done = sum(1 for s, t in tasks
               if progress.get(s, {}).get(t, {}).get("status") == "pass")
    st.sidebar.caption(f"{done}/{len(tasks)} tasks passed")

    try:
        spec = load_spec(sprint, task, default_tasks_root(REPO_ROOT))
    except SpecError as exc:
        st.error(f"Task spec error: {exc}")
        return

    st.title(spec.title)
    st.caption(f"{sprint} / {task}")

    submission = REPO_ROOT / spec.submission_path

    col_lesson, col_work = st.columns([1, 1])

    with col_lesson:
        st.subheader("Lesson")
        lesson_file = spec.task_dir / "lesson.md"
        if lesson_file.is_file():
            st.markdown(lesson_file.read_text())
        elif spec.scaffold:
            st.markdown("Read the instructions in the scaffold, then write your solution.")
            st.code((spec.task_dir / spec.scaffold).read_text(), language="sql")
        else:
            st.info("No lesson text for this task yet.")

    with col_work:
        st.subheader("Your work")
        if not submission.exists():
            st.info(f"Not started. Copy the scaffold into `{spec.submission_path}`.")
            if st.button("Start this task"):
                start(sprint, task, REPO_ROOT, overwrite=False)
                st.rerun()
        else:
            current = submission.read_text()
            edited = st.text_area("Edit and save your submission", value=current,
                                  height=260, key=f"editor-{sprint}-{task}")
            c1, c2 = st.columns(2)
            if c1.button("💾 Save"):
                submission.write_text(edited)
                st.success("Saved.")
            if c2.button("✅ Check my work", type="primary"):
                submission.write_text(edited)  # grade what's on screen
                result = run_check(sprint, task, REPO_ROOT, make_proof=True)
                _render_result(result)


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
                   "Start it with `docker compose up -d` and try again.")
    else:
        st.error("Not yet — fix the items above and check again.")


if __name__ == "__main__":
    main()
