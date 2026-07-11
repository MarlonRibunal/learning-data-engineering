## Failure is normal — design for it

In distributed systems, transient failure isn't an exception, it's the weather: a
network blip, a rate limit, a database mid-restart. Mature pipelines assume it and
recover automatically. Setting `retries` on a task is the first line of that
defense.

The mechanics and the trade-offs:

- **Retries + backoff.** `retries=3` with `retry_delay` (ideally exponential —
  the pattern you built in the Production sprint) gives the downstream time to
  recover instead of hammering it. Retry a *transient* error; don't retry a
  *permanent* one (a bad query will fail three times, slower).

- **At-least-once → idempotency.** Retries mean a task might run more than once.
  Combined with backfills, this is why tasks *must* be idempotent — "at least
  once" execution only produces correct data if running twice equals running once.

- **Alerting.** Retries buy resilience, but silent retries hide chronic problems.
  Airflow can fire on failure (email, Slack, PagerDuty) so a task that's
  *retrying every night* still surfaces to a human.

- **SLAs.** You can declare how long a task *should* take; blow past it and
  Airflow flags it — freshness monitoring built into the orchestrator.

So `retries` is a small setting standing in for a big principle: build pipelines
that heal themselves for the routine failures, and shout loudly for the real ones.

*Go deeper: Airflow retries, callbacks/alerting, SLAs; "at-least-once" semantics.*
