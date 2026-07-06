"""Check-type registry.

The extensibility seam. Each check kind is a CheckType subclass registered under
a string key. A task's YAML lists checks by ``type``; the core looks each one up
here and runs it. Adding a NEW task = writing YAML only. Adding a new KIND of
check = one subclass + one ``@register`` line, nothing else.
"""

from __future__ import annotations

from typing import Callable, Type

from .context import Context
from .result import CheckResult, Status

REGISTRY: dict[str, Type["CheckType"]] = {}


class CheckType:
    """Base class for all checks.

    A CheckType is instantiated with its slice of the task spec (the YAML dict
    for one check entry) and then ``run`` against a Context. It must never raise
    for a wrong-answer condition — return a FAIL CheckResult instead. It should
    only let infra problems surface as ERROR (see ``run`` wrappers below).
    """

    type_key: str = ""

    def __init__(self, spec: dict):
        self.spec = spec
        self.name = spec.get("name") or self.type_key

    def run(self, ctx: Context) -> CheckResult:  # pragma: no cover - abstract
        raise NotImplementedError

    # Convenience constructors so subclasses read cleanly.
    def _pass(self, hint: str = "") -> CheckResult:
        return CheckResult(self.name, Status.PASS, hint)

    def _fail(self, hint: str) -> CheckResult:
        return CheckResult(self.name, Status.FAIL, hint)

    def _error(self, hint: str) -> CheckResult:
        return CheckResult(self.name, Status.ERROR, hint)


def register(type_key: str) -> Callable[[Type[CheckType]], Type[CheckType]]:
    def deco(cls: Type[CheckType]) -> Type[CheckType]:
        if type_key in REGISTRY:
            raise ValueError(f"check type already registered: {type_key!r}")
        cls.type_key = type_key
        REGISTRY[type_key] = cls
        return cls

    return deco


def build_check(spec: dict) -> CheckType:
    """Instantiate the CheckType for one check spec. Raises on unknown type."""
    type_key = spec.get("type")
    if not type_key:
        raise KeyError("check spec is missing a 'type' field")
    try:
        cls = REGISTRY[type_key]
    except KeyError as exc:
        known = ", ".join(sorted(REGISTRY)) or "(none registered)"
        raise KeyError(
            f"unknown check type {type_key!r}; known types: {known}"
        ) from exc
    return cls(spec)
