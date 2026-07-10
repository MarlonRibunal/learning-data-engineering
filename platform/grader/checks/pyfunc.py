"""Generic Python-function check: import a function, call it, compare its return.

For pure-Python tasks — no Spark, no DB. The learner writes a function; the
grader imports it, calls it with the spec's ``args``, and compares the return
value with ``expect`` (numbers normalized so 34 == 34.0).

    entry: str     function name (required)
    args: list     positional args to call it with (default [])
    expect: any    expected return value (dict / list / scalar)

    PASS  - the return value matches
    FAIL  - the learner's code errored or returned the wrong value
"""

from __future__ import annotations

import importlib.util
from decimal import Decimal

from ..context import Context
from ..registry import CheckType, register
from ..result import CheckResult

_MISSING = object()


def _load_fn(path, name):
    spec = importlib.util.spec_from_file_location("pyfunc_submission", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # bad learner code raises — caller catches
    return getattr(mod, name, _MISSING)


def _norm(value):
    """Recursively normalize numbers so int/float/Decimal compare by value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return round(float(value), 6)
    if isinstance(value, dict):
        return {k: _norm(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value]
    return value


@register("pyfunc")
class PyFuncCheck(CheckType):
    def run(self, ctx: Context) -> CheckResult:
        entry = self.spec.get("entry")
        if not entry:
            return self._error("task spec is missing `entry` (the function name)")
        args = self.spec.get("args", [])
        expect = self.spec.get("expect")

        try:
            fn = _load_fn(ctx.submission_path, entry)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your code failed to import: {exc}")
        if fn is _MISSING:
            return self._fail(f"define a function named `{entry}(...)`")
        if not callable(fn):
            return self._fail(f"`{entry}` must be a function")

        try:
            got = fn(*args)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"your function errored: {exc}")

        if _norm(got) != _norm(expect):
            return self._fail(f"expected {expect!r}, but your function returned {got!r}")
        return self._pass()
