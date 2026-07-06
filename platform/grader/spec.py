"""Task spec loading.

A task lives at ``<tasks_root>/<sprint>/<task>/spec.yml`` and looks like:

    title: Build the top-customers view
    submission_path: submissions/top_customers.sql
    scaffold: scaffold/top_customers.sql      # optional
    solution: solution/top_customers.sql      # optional, reference only
    checks:
      - type: file_contains
        name: selects from customers
        pattern: "(?i)from\\s+customers"

``submission_path`` is where the learner's work lives, relative to the repo root.
``scaffold`` (relative to the task dir) is copied there by ``check start``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


class SpecError(ValueError):
    """Raised when a task spec is missing, malformed, or incomplete."""


@dataclass
class TaskSpec:
    sprint: str
    task: str
    task_dir: Path
    title: str
    submission_path: str
    checks: list[dict] = field(default_factory=list)
    scaffold: str | None = None
    solution: str | None = None
    reseed: str | None = None  # SQL file (repo-root relative) to load before checks
    proof: dict | None = None  # portfolio-artifact config, emitted on pass


def load_spec(sprint: str, task: str, tasks_root: Path) -> TaskSpec:
    task_dir = tasks_root / sprint / task
    spec_file = task_dir / "spec.yml"
    if not spec_file.is_file():
        raise SpecError(f"no task spec at {spec_file}")

    import yaml  # lazily imported so `--help` etc. work without PyYAML

    try:
        raw = yaml.safe_load(spec_file.read_text()) or {}
    except yaml.YAMLError as exc:
        raise SpecError(f"malformed YAML in {spec_file}: {exc}") from exc

    if not isinstance(raw, dict):
        raise SpecError(f"{spec_file} must be a YAML mapping, got {type(raw).__name__}")

    missing = [k for k in ("title", "submission_path", "checks") if k not in raw]
    if missing:
        raise SpecError(f"{spec_file} is missing required field(s): {', '.join(missing)}")

    checks = raw["checks"]
    if not isinstance(checks, list) or not checks:
        raise SpecError(f"{spec_file}: 'checks' must be a non-empty list")

    return TaskSpec(
        sprint=sprint,
        task=task,
        task_dir=task_dir,
        title=str(raw["title"]),
        submission_path=str(raw["submission_path"]),
        checks=checks,
        scaffold=raw.get("scaffold"),
        solution=raw.get("solution"),
        reseed=raw.get("reseed"),
        proof=raw.get("proof"),
    )
