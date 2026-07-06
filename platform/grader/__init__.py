"""Learn-by-doing grader.

Public API:

    from grader import run_check, start, Result, Status

The grader checks a learner's real data-engineering work against declarative
YAML task specs. The same engine backs both the CLI (`scripts/check.sh`) and the
Streamlit lesson-runner — the UI is a thin shell over ``run_check``.
"""

from __future__ import annotations

from .core import discover_tasks, next_task, run_check, start
from .result import CheckResult, Result, Status
from .spec import SpecError

__all__ = [
    "run_check", "start", "discover_tasks", "next_task",
    "Result", "CheckResult", "Status", "SpecError",
]
