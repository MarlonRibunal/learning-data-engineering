### Chain tasks with a dependency

Real pipelines have steps that must run **in order** — you can't load data you haven't
extracted yet. In Airflow you express that with `>>` (upstream `>>` downstream).

**Your task:** the `two_step_pipeline` DAG has an `extract` task and a `load` task. Make
it run green:

1. `load` currently raises — make it finish normally (return a value).
2. Wire the order so extract runs first: `extract_task >> load_task`.

```
extract_task >> load_task   # extract, then load
```

When you check, the grader triggers the real DAG and also confirms you set the
dependency. Green means a real two-step pipeline ran in the right order.

> Needs the stack: `./platform.sh up` first.
