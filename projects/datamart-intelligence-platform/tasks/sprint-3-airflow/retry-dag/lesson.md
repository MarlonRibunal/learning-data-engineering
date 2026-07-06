### Make tasks resilient with retries

Real pipelines hit transient failures — a network blip, a database that's briefly busy.
Instead of failing the whole run, Airflow can **retry** a task a few times first.

**Your task:** give the `work` task retries so a transient failure is retried instead of
failing immediately.

```
PythonOperator(task_id="work", python_callable=do_work, retries=2)
```

You can also set it for every task at once via the DAG's `default_args`. Retries are one
of the cheapest reliability wins in orchestration.

> Needs the stack: `./platform.sh up` first.
