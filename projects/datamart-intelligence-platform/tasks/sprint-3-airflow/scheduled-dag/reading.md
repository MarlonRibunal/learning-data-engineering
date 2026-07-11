## Scheduling, data intervals, and backfill

Setting a `schedule` looks simple, but it hides Airflow's most powerful (and most
confusing) idea: a DAG run is tied to a **data interval**, not to wall-clock time.

When a DAG scheduled `@daily` runs, it isn't "the run for right now" — it's the
run responsible for a *specific past interval* (say, all of yesterday). Airflow
runs it **after** that interval closes, and passes the interval's boundaries into
your tasks (the "logical date"). Your task should process *that interval's data*,
not `now()`.

Why this design is brilliant:

- **Backfill.** Because each run owns a date range, Airflow can run history. Point
  a new DAG at last year with `catchup=True` and it executes one run per interval,
  in order, filling the past — using the exact same task code.
- **Reproducibility.** Re-running "the 2026-03-01 run" reprocesses March 1st's
  data, every time, no matter when you click it. (This is why idempotency
  matters — a backfill re-runs intervals that already ran.)
- **Determinism.** Tasks keyed to a logical date don't depend on when the machine
  happened to be up.

So a schedule isn't just "run it every night" — it's "own this stream of time
intervals, and be able to (re)compute any of them on demand."

*Go deeper: Airflow "DAG runs & data intervals", `catchup`, and backfilling.*
