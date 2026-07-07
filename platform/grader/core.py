"""Grader core: orchestration.

    check(sprint, task) -> Result

Loads the task spec, dispatches each check via the registry, aggregates into a
Result, and records progress. ``start`` copies a task's scaffold into the
learner's submission path so they edit a stub, not the shipped solution.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import checks as _checks  # noqa: F401 - registers built-in check types
from . import progress
from .context import (
    CommandRunner,
    Context,
    Database,
    InfraError,
    LocalRunner,
    PostgresDatabase,
)
from .registry import build_check
from .result import CheckResult, Result, Status
from .spec import SpecError, load_spec

DEFAULT_TASKS_ROOT = "projects/datamart-intelligence-platform/tasks"


def default_tasks_root(repo_root: Path) -> Path:
    return repo_root / DEFAULT_TASKS_ROOT


def discover_tasks(repo_root: Path, tasks_root: Path | None = None) -> list[tuple[str, str]]:
    """Return (sprint, task) pairs discovered from spec.yml files, sprint-ordered.

    Shared by the CLI (`check list`) and the Streamlit runner so both show the
    same task list in the same order.
    """
    root = tasks_root or default_tasks_root(repo_root)
    if not root.is_dir():
        return []
    triples = []
    for spec_file in root.glob("*/*/spec.yml"):
        sprint, task = spec_file.parent.parent.name, spec_file.parent.name
        triples.append((sprint, task, _read_order(spec_file)))
    triples.sort(key=lambda x: (_sprint_rank(x[0]), x[0], x[2], x[1]))
    return [(sprint, task) for sprint, task, _ in triples]


def _read_order(spec_file: Path) -> int:
    """Read just the task's `order` for sorting (default 100). Never raises."""
    try:
        import yaml
        data = yaml.safe_load(spec_file.read_text()) or {}
        return int(data.get("order", 100))
    except Exception:  # noqa: BLE001 - a broken spec shouldn't break discovery
        return 100


# Curriculum order: fundamentals, then the lifecycle sprints, capstone last.
_SPRINT_ORDER = ["sql-fundamentals", "ingestion", "sprint-2-dbt",
                 "data-quality", "sprint-3-airflow", "serving", "streaming"]


def _sprint_rank(sprint: str) -> tuple[int, int]:
    if sprint in _SPRINT_ORDER:
        return (0, _SPRINT_ORDER.index(sprint))
    if sprint == "capstone":
        return (2, 0)
    return (1, 0)  # unknown sprints sit between the known ones and the capstone


def next_task(repo_root: Path, tasks_root: Path | None = None) -> tuple[str, str] | None:
    """First task (in curriculum order) the learner hasn't passed yet, or None."""
    prog = progress.load(repo_root)
    for sprint, task in discover_tasks(repo_root, tasks_root):
        if prog.get(sprint, {}).get(task, {}).get("status") != "pass":
            return (sprint, task)
    return None


def run_check(
    sprint: str,
    task: str,
    repo_root: Path,
    *,
    tasks_root: Path | None = None,
    db: Database | None = None,
    runner: CommandRunner | None = None,
    record_progress: bool = True,
    make_proof: bool = False,
) -> Result:
    tasks_root = tasks_root or default_tasks_root(repo_root)
    spec = load_spec(sprint, task, tasks_root)
    submission_path = repo_root / spec.submission_path
    db = db if db is not None else PostgresDatabase()
    runner = runner if runner is not None else LocalRunner(repo_root)
    ctx = Context(
        repo_root=repo_root,
        task_dir=spec.task_dir,
        submission_path=submission_path,
        db=db,
        runner=runner,
        solution_path=(spec.task_dir / spec.solution) if spec.solution else None,
    )

    # Reseed source data first so real-infra checks are deterministic
    # (reseed-before / assert-after). File-only tasks omit `reseed` and never
    # touch the DB. A reseed failure is infra, not a learner failure.
    if spec.reseed:
        reseed_file = _resolve_reseed(spec.reseed, spec.task_dir, repo_root)
        try:
            db.execute_script(reseed_file.read_text())
        except InfraError as exc:
            result = Result(sprint, task,
                            [CheckResult("reseed source data", Status.ERROR, str(exc))])
            if record_progress:
                progress.record(repo_root, sprint, task, result.status.value)
            return result

    results = []
    for check_spec in spec.checks:
        try:
            check = build_check(check_spec)
        except KeyError as exc:
            # A broken task spec is an authoring error, not a learner failure.
            raise SpecError(str(exc)) from exc
        results.append(check.run(ctx))

    result = Result(sprint=sprint, task=task, checks=results)

    # On a passing task that defines a `proof`, emit the portfolio artifact —
    # the shareable "I actually built this" moment.
    if make_proof and result.passed and spec.proof:
        from . import proof as _proof  # local import avoids a module cycle
        result.proof_dir = _proof.generate_proof(sprint, task, spec, result, ctx, repo_root)

    if record_progress:
        progress.record(repo_root, sprint, task, result.status.value)
    return result


def _resolve_reseed(reseed: str, task_dir: Path, repo_root: Path) -> Path:
    """A reseed path may be given relative to the task dir or the repo root."""
    candidate = task_dir / reseed
    if candidate.is_file():
        return candidate
    root_candidate = repo_root / reseed
    if root_candidate.is_file():
        return root_candidate
    raise SpecError(f"reseed file not found: {reseed}")


def start(
    sprint: str,
    task: str,
    repo_root: Path,
    *,
    tasks_root: Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy a task's scaffold into its submission path so the learner can edit it."""
    tasks_root = tasks_root or default_tasks_root(repo_root)
    spec = load_spec(sprint, task, tasks_root)
    if not spec.scaffold:
        raise SpecError(f"task {sprint}/{task} has no 'scaffold' to start from")

    src = spec.task_dir / spec.scaffold
    if not src.is_file():
        raise SpecError(f"scaffold file not found: {src}")

    dst = repo_root / spec.submission_path
    if dst.exists() and not overwrite:
        raise FileExistsError(
            f"{dst} already exists — pass overwrite to reset it to the scaffold"
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return dst
