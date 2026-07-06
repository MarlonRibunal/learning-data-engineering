### Capstone: ship an analytics platform

This ties everything together. You'll prove that a real, end-to-end data platform
works — the exact shape most data-engineering jobs are built around:

```
raw orders ──▶ dbt (transform + test) ──▶ analytics table ──▶ Airflow (orchestrate) ──▶ dashboard
```

**Prerequisites:** finish `sprint-2-dbt/revenue-by-status` (the dbt mart) and
`sprint-3-airflow/hello-dag` (the DAG). The capstone re-verifies both **together**
against the real stack.

When every check passes, the grader writes you a **portfolio artifact** under
`portfolio/` — a `PORTFOLIO.md` describing what you built, the verified checks, and
a chart of your real result. Commit it to your own GitHub. That folder is proof you
built and verified a real pipeline, not a tutorial you watched.

> Needs the stack running: `docker compose up -d` first.
