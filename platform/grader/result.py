"""Result types for the grader.

A check has one of three outcomes:

    PASS  - the learner's work satisfies the check
    FAIL  - the learner's work is wrong (a real, actionable failure)
    ERROR - the grader could not decide because infrastructure was unavailable
            (Postgres down, container missing). This is NOT the learner's fault.

Distinguishing ERROR from FAIL is deliberate: telling a correct learner "you're
wrong" because a container was asleep is the worst failure mode for a learning
tool. Overall status surfaces ERROR over FAIL for exactly that reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


@dataclass
class CheckResult:
    name: str
    status: Status
    hint: str = ""

    @property
    def ok(self) -> bool:
        return self.status is Status.PASS


@dataclass
class Result:
    sprint: str
    task: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def status(self) -> Status:
        # ERROR wins over FAIL: never report "wrong" when the truth is "couldn't run".
        if any(c.status is Status.ERROR for c in self.checks):
            return Status.ERROR
        if any(c.status is Status.FAIL for c in self.checks):
            return Status.FAIL
        return Status.PASS

    @property
    def passed(self) -> bool:
        return self.status is Status.PASS
