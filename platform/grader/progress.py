"""Local progress tracking.

State lives in a single git-ignored JSON file at the repo root. No database, no
account. Shape:

    {"<sprint>": {"<task>": {"status": "pass", "last_run": "...", "attempts": 3}}}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROGRESS_FILENAME = ".progress.json"


def _path(repo_root: Path) -> Path:
    return repo_root / PROGRESS_FILENAME


def load(repo_root: Path) -> dict:
    path = _path(repo_root)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text() or "{}")
    except json.JSONDecodeError:
        # Corrupt progress should never block grading; start fresh.
        return {}


def record(repo_root: Path, sprint: str, task: str, status: str, *, now=None) -> dict:
    data = load(repo_root)
    sprint_state = data.setdefault(sprint, {})
    task_state = sprint_state.setdefault(task, {"attempts": 0})
    task_state["attempts"] = task_state.get("attempts", 0) + 1
    task_state["status"] = status
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    task_state["last_run"] = stamp
    _path(repo_root).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return data


def hints_shown(repo_root: Path, sprint: str, task: str) -> int:
    """How many progressive hints the learner has revealed for a task so far.

    Persisted alongside progress so an escalating hint ladder survives a
    power-down — the same promise as everything else in the container.
    """
    return int(load(repo_root).get(sprint, {}).get(task, {}).get("hints_shown", 0))


def reveal_hint(repo_root: Path, sprint: str, task: str) -> int:
    """Reveal one more hint for a task; return the new revealed count."""
    data = load(repo_root)
    task_state = data.setdefault(sprint, {}).setdefault(task, {"attempts": 0})
    task_state["hints_shown"] = task_state.get("hints_shown", 0) + 1
    _path(repo_root).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return task_state["hints_shown"]
