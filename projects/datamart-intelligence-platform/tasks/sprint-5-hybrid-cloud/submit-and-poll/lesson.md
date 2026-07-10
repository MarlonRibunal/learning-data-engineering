# Submit and poll

An external job is **asynchronous**: submitting it returns immediately with a
handle, long before the work is done. Your orchestrator has to wait for it.

```python
def run_and_wait(client, job_id):
    run_id = client.submit(job_id)
    while True:
        status = client.get_status(run_id)
        if status in ("SUCCESS", "FAILED"):
            break
    return client.get_result(run_id)
```

- **`client.submit(job_id)`** starts the run and returns a `run_id`.
- **`client.get_status(run_id)`** returns `"RUNNING"`, `"SUCCESS"`, or `"FAILED"`. You must **poll** — call it repeatedly until the run reaches a terminal state.
- **`client.get_result(run_id)`** gives the output once it's done.

(In production you'd `time.sleep(...)` between polls so you don't hammer the API — the grader's mock finishes fast, so you don't need to here.)

## Your task

Write `run_and_wait(client, job_id)` that submits the job, polls until it finishes, and **returns the result** from `client.get_result(...)`. (Failure handling comes in the next level.)
