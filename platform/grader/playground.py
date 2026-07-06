"""Run a learner's SQL against the real warehouse and return the rows.

Powers the "Run" button in the lesson-runner: the learner sees what their query
actually returns before they check it — a real SQL playground, not pattern-matching.

Safety: the query runs in a READ-ONLY transaction with a short statement timeout,
so a learner can explore freely without mutating or hanging the warehouse. The raw
source tables are reseeded first (idempotently) and `search_path` is set to `raw`
so unqualified names like `FROM orders` resolve.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .context import InfraError, _dsn_from_env

DEFAULT_SEED = "projects/datamart-intelligence-platform/seeds/raw_seed.sql"
ROW_LIMIT = 200


@dataclass
class QueryResult:
    columns: list[str] = field(default_factory=list)
    rows: list[tuple] = field(default_factory=list)
    error: str | None = None       # a SQL error in the learner's query (shown to them)
    truncated: bool = False        # more rows existed than ROW_LIMIT

    @property
    def as_records(self) -> list[dict]:
        return [dict(zip(self.columns, row)) for row in self.rows]


def run_sql(repo_root: Path, sql: str, *, seed_file: str = DEFAULT_SEED,
            limit: int = ROW_LIMIT) -> QueryResult:
    """Execute read-only SQL against the seeded warehouse. Raises InfraError if the
    stack is unreachable; a bad query comes back as QueryResult.error (not an raise)."""
    try:
        import psycopg2
        from psycopg2 import Error as PgError
    except ImportError as exc:  # pragma: no cover
        raise InfraError("psycopg2 is not installed") from exc

    if not sql or not sql.strip():
        return QueryResult(error="write a query first")

    try:
        conn = psycopg2.connect(**_dsn_from_env())
    except Exception as exc:  # noqa: BLE001 - any connect failure is infra
        raise InfraError(f"could not connect to Postgres — is the stack up? ({exc})") from exc

    try:
        # Reseed the raw tables (write) so the playground is deterministic.
        seed_path = repo_root / seed_file
        if seed_path.is_file():
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(seed_path.read_text())

        # Run the learner's query read-only.
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("SET LOCAL statement_timeout = '5s'")
            cur.execute("SET LOCAL search_path TO raw, public")
            try:
                cur.execute(sql)
            except PgError as exc:
                conn.rollback()
                return QueryResult(error=str(exc).strip())
            if cur.description is None:
                conn.rollback()
                return QueryResult(error="that statement returned no result set — "
                                         "write a SELECT query")
            columns = [d[0] for d in cur.description]
            rows = cur.fetchmany(limit + 1)
        conn.rollback()
        truncated = len(rows) > limit
        return QueryResult(columns=columns, rows=rows[:limit], truncated=truncated)
    finally:
        conn.close()
