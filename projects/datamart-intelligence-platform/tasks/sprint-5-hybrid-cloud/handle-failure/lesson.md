# Fail loudly

A pipeline that keeps going after an upstream job **failed** is worse than one
that stops — it silently ships wrong or missing data downstream. So the golden
rule of orchestrating external jobs: **if the run fails, raise.**

```python
def run_and_wait(client, job_id):
    run_id = client.submit(job_id)
    while True:
        status = client.get_status(run_id)
        if status == "SUCCESS":
            return client.get_result(run_id)
        if status == "FAILED":
            raise RuntimeError(f"job {job_id} failed")
```

Raising is what makes Airflow mark the task **failed**, stop dependent tasks, and fire your alerts — instead of the DAG going green on a broken run.

## Your task

Extend `run_and_wait(client, job_id)` so it:

- **returns** `client.get_result(run_id)` when the run ends `"SUCCESS"`, and
- **raises** an exception when the run ends `"FAILED"`.
