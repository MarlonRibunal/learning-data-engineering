"""Helpers for driving the Docker Compose stack from the host.

The grader never re-implements dbt or Airflow — it shells into the running
service containers via `docker compose exec`. These helpers build those command
lines and, crucially, tell an *infrastructure* failure ("the stack is down")
apart from a *learner* failure ("your dbt test failed"). Getting that distinction
right is what stops the grader telling a correct learner they're wrong.
"""

from __future__ import annotations

# Substrings that mean "the stack/tooling was unavailable", not "the work is wrong".
_INFRA_SIGNS = (
    "no such service",
    "not running",
    "cannot connect to the docker daemon",
    "is the docker daemon running",
    "connection refused",
    "could not connect",
    "could not translate host name",
    "name or service not known",
    "no such container",
    "error response from daemon",
)


def looks_like_infra(text: str) -> bool:
    lowered = text.lower()
    return any(sign in lowered for sign in _INFRA_SIGNS)


def compose_exec(service: str, *cmd: str) -> list[str]:
    """Build a `docker compose exec -T <service> <cmd...>` argument list."""
    return ["docker", "compose", "exec", "-T", service, *cmd]


def tail(text: str, lines: int = 15) -> str:
    """Last N non-empty lines of command output, for concise hints."""
    kept = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(kept[-lines:])
