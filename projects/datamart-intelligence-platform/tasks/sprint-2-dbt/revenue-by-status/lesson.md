### Build a dbt mart: revenue by status

You have raw orders. Turn them into a clean, tested analytics table with **dbt** —
the tool most modern data teams use for transformations.

**Your task:** complete the `revenue_by_status` model so it returns one row per
order `status` with the total revenue for that status.

- Read from `{{ source('raw', 'orders') }}`.
- Revenue is `SUM(total_amount)`.
- One row per `status` means `GROUP BY status`.

When you check, the grader runs **`dbt build`** in the real dbt container: it
materializes your model *and* runs its tests (`status` is unique + not null,
`revenue` is not null). Green means your model is correct AND passes data-quality
checks — the same bar a real data team holds.

> Needs the stack running: `docker compose up -d` first.
