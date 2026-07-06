"""Runtime context handed to each check.

The Context carries everything a check needs to inspect the learner's work:
the repo root, the task directory, the resolved submission path, and a Database
handle. Checks never open their own connections or resolve their own paths — the
core builds one Context and passes it in, which keeps checks pure and testable
(unit tests inject a fake Database).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class InfraError(RuntimeError):
    """Raised when infrastructure (e.g. Postgres) is unreachable.

    Checks catch this and report Status.ERROR rather than Status.FAIL, so a
    sleeping container never tells a correct learner they got it wrong.
    """


class Database(Protocol):
    def query(self, sql: str, params: tuple | None = None) -> list[tuple]:
        """Run a read query and return rows. Raise InfraError if unreachable."""
        ...

    def execute_script(self, sql: str) -> None:
        """Run one or more statements (DDL/DML) and commit. Raise InfraError on failure."""
        ...


@dataclass
class RunResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def output(self) -> str:
        return f"{self.stdout}\n{self.stderr}".strip()


class CommandRunner(Protocol):
    def run(self, args: list[str], timeout: float | None = None) -> RunResult:
        """Run a subprocess. Raise InfraError if the command cannot start or times out."""
        ...


class LocalRunner:
    """Runs commands on the host (e.g. `docker compose exec ...`)."""

    def __init__(self, cwd: Path):
        self.cwd = cwd

    def run(self, args: list[str], timeout: float | None = None) -> RunResult:
        import subprocess

        try:
            proc = subprocess.run(
                args, cwd=str(self.cwd),
                capture_output=True, text=True, timeout=timeout,
            )
        except FileNotFoundError as exc:
            raise InfraError(f"command not found: {args[0]} ({exc})") from exc
        except subprocess.TimeoutExpired as exc:
            raise InfraError(
                f"command timed out after {timeout}s: {' '.join(args)}"
            ) from exc
        return RunResult(proc.returncode, proc.stdout or "", proc.stderr or "")


@dataclass
class Context:
    repo_root: Path
    task_dir: Path
    submission_path: Path
    db: Database
    runner: CommandRunner | None = None


class PostgresDatabase:
    """Real Postgres handle. Connects lazily so a task that uses no SQL checks
    never needs the stack running. A connection failure surfaces as InfraError."""

    def __init__(self, dsn: dict | None = None):
        self._dsn = dsn or _dsn_from_env()
        self._conn = None

    def _connect(self):
        if self._conn is not None:
            return self._conn
        try:
            import psycopg2  # imported lazily; only needed for SQL checks
        except ImportError as exc:  # pragma: no cover - environment issue
            raise InfraError(
                "psycopg2 is not installed; install platform/requirements.txt"
            ) from exc
        try:
            self._conn = psycopg2.connect(**self._dsn)
        except Exception as exc:  # noqa: BLE001 - any connect failure is infra
            raise InfraError(
                f"could not connect to Postgres at "
                f"{self._dsn.get('host')}:{self._dsn.get('port')} — is the stack up? "
                f"({exc})"
            ) from exc
        return self._conn

    def query(self, sql: str, params: tuple | None = None) -> list[tuple]:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception as exc:  # noqa: BLE001
            # A broken connection is infra; a bad query is the check's problem
            # and should be handled by the check, but we cannot tell them apart
            # reliably here, so surface as InfraError and let the check decide.
            raise InfraError(f"query failed: {exc}") from exc

    def execute_script(self, sql: str) -> None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            conn.rollback()
            raise InfraError(f"script failed: {exc}") from exc


def _dsn_from_env() -> dict:
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", "5432")),
        "dbname": os.environ.get("POSTGRES_DB", "datamart"),
        "user": os.environ.get("POSTGRES_USER", "airflow"),
        "password": os.environ.get("POSTGRES_PASSWORD", "airflow"),
    }
