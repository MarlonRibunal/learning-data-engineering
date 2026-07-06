"""Command-line entrypoint: `python -m grader ...` (wrapped by scripts/check.sh).

    check <sprint> <task>    grade the learner's submission
    start <sprint> <task>    copy the task scaffold into the submission path

Exit codes: 0 = pass, 1 = fail, 2 = error (infra) or broken task spec.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import progress
from .core import discover_tasks, run_check, start
from .result import Status
from .spec import SpecError

# ANSI colors, disabled when stdout is not a TTY.
_TTY = sys.stdout.isatty()
_GREEN = "\033[32m" if _TTY else ""
_RED = "\033[31m" if _TTY else ""
_YELLOW = "\033[33m" if _TTY else ""
_DIM = "\033[2m" if _TTY else ""
_RESET = "\033[0m" if _TTY else ""

_MARK = {
    Status.PASS: f"{_GREEN}PASS{_RESET}",
    Status.FAIL: f"{_RED}FAIL{_RESET}",
    Status.ERROR: f"{_YELLOW} ?? {_RESET}",
}


def _resolve_repo_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    # Walk up looking for the repo marker (docker-compose.yml at the root).
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "docker-compose.yml").is_file():
            return candidate
    return here


def _cmd_check(args) -> int:
    repo_root = _resolve_repo_root(args.repo_root)
    try:
        result = run_check(args.sprint, args.task, repo_root, make_proof=True)
    except SpecError as exc:
        print(f"{_RED}task error:{_RESET} {exc}", file=sys.stderr)
        return 2

    print(f"{_DIM}{args.sprint}/{args.task}{_RESET}")
    for check in result.checks:
        mark = _MARK.get(check.status, "?")
        line = f"  {mark} {check.name}"
        if check.hint and check.status is not Status.PASS:
            line += f"  {_DIM}— {check.hint}{_RESET}"
        print(line)

    if result.status is Status.PASS:
        print(f"{_GREEN}PASS{_RESET} — nice work.")
        if result.proof_dir is not None:
            rel = result.proof_dir.relative_to(repo_root)
            print(f"{_GREEN}🎉 Portfolio artifact written to {rel}{_RESET} — "
                  f"commit it to your GitHub to show what you built.")
        return 0
    if result.status is Status.ERROR:
        print(f"{_YELLOW}COULD NOT RUN{_RESET} — infrastructure is unavailable, "
              f"not your work. Is the stack up? `docker compose up -d`")
        return 2
    print(f"{_RED}FAIL{_RESET} — fix the items above and run again.")
    return 1


def _cmd_start(args) -> int:
    repo_root = _resolve_repo_root(args.repo_root)
    try:
        dst = start(args.sprint, args.task, repo_root, overwrite=args.overwrite)
    except SpecError as exc:
        print(f"{_RED}task error:{_RESET} {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"{_YELLOW}{exc}{_RESET}", file=sys.stderr)
        return 2
    rel = dst.relative_to(repo_root)
    print(f"Started {args.sprint}/{args.task}. Edit {_GREEN}{rel}{_RESET}, "
          f"then run: check {args.sprint} {args.task}")
    return 0


def _cmd_list(args) -> int:
    repo_root = _resolve_repo_root(args.repo_root)
    tasks = discover_tasks(repo_root)
    if not tasks:
        print("No tasks found.")
        return 0
    prog = progress.load(repo_root)
    mark = {"pass": f"{_GREEN}pass{_RESET}", "fail": f"{_RED}fail{_RESET}",
            "error": f"{_YELLOW}err {_RESET}"}
    passed = 0
    current = None
    for sprint, task in tasks:
        if sprint != current:
            print(f"\n{_DIM}{sprint}{_RESET}")
            current = sprint
        status = prog.get(sprint, {}).get(task, {}).get("status")
        if status == "pass":
            passed += 1
        print(f"  [{mark.get(status, '    ')}]  {task}")
    print(f"\n{passed}/{len(tasks)} passed. "
          f"Start one with: check start <sprint> <task>")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check", description="Learn-by-doing grader")
    parser.add_argument("--repo-root", help="repo root (default: auto-detect)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="grade a task submission")
    p_check.add_argument("sprint")
    p_check.add_argument("task")
    p_check.set_defaults(func=_cmd_check)

    p_start = sub.add_parser("start", help="copy a task scaffold into your workspace")
    p_start.add_argument("sprint")
    p_start.add_argument("task")
    p_start.add_argument("--overwrite", action="store_true",
                         help="reset an existing submission back to the scaffold")
    p_start.set_defaults(func=_cmd_start)

    p_list = sub.add_parser("list", help="list all tasks and your progress")
    p_list.set_defaults(func=_cmd_list)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
