### Your first dbt model: count orders per status

You wrote SQL against a live database in Sprint 1. **dbt** takes that same SQL and
turns it into a managed, tested table in the warehouse — versioned, documented, and
checked on every run.

**Your task:** complete the `orders_per_status` model so it returns one row per
`status` with the number of orders in that status.

- Read from `{{ source('raw', 'orders') }}` (dbt's reference to the raw table).
- `COUNT(*)` counts rows; `GROUP BY status` gives one row per status.

`dbt build` will materialize your model **and** run its tests (status unique + not
null). Green means correct data *and* passing data-quality checks.

> Needs the stack: `./platform.sh up` first.
