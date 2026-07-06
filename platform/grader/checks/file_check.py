"""File-based check types.

Cheap checks that need no running stack, so early sprints grade instantly.
They inspect the learner's submission file directly.
"""

from __future__ import annotations

import re

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult


@register("file_exists")
class FileExists(CheckType):
    """Pass if the submission file exists and is non-empty."""

    def run(self, ctx: Context) -> CheckResult:
        path = ctx.submission_path
        if not path.is_file():
            return self._fail(f"expected a file at {path} — run `check start` first, then edit it")
        if path.stat().st_size == 0:
            return self._fail(f"{path.name} is empty — write your solution in it")
        return self._pass()


@register("file_contains")
class FileContains(CheckType):
    """Pass if the submission file matches a regex pattern.

    Spec keys:
        pattern:  a Python regex (required)
        hint:     custom message shown on failure (optional)
    """

    def run(self, ctx: Context) -> CheckResult:
        pattern = self.spec.get("pattern")
        if not pattern:
            return self._fail("task spec error: file_contains needs a 'pattern'")
        path = ctx.submission_path
        if not path.is_file():
            return self._fail(f"expected a file at {path} — run `check start` first")
        text = path.read_text()
        if re.search(pattern, text):
            return self._pass()
        hint = self.spec.get("hint") or f"{path.name} should match /{pattern}/"
        return self._fail(hint)
