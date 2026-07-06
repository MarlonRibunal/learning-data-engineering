### Put a pipeline on a schedule

A pipeline that only runs when you click "trigger" isn't automation. Airflow runs a DAG
on whatever cadence you set with `schedule_interval` — a preset like `@daily` / `@hourly`,
or a cron string like `"0 6 * * *"` (6am daily).

**Your task:** the `scheduled_report` DAG works, but its `schedule_interval` is `None`
(manual-only). Give it a real schedule:

```
schedule_interval="@daily"
```

When you check, the grader runs the DAG and confirms you set a schedule. Setting the
cadence is the difference between a script and a pipeline.

> Needs the stack: `./platform.sh up` first.
