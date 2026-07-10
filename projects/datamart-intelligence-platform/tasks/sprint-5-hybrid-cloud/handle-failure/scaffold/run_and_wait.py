def run_and_wait(client, job_id):
    # This waits for the run, but treats a FAILED run as if it succeeded.
    # TODO: raise an exception when the status is FAILED instead.
    run_id = client.submit(job_id)
    while True:
        status = client.get_status(run_id)
        if status in ("SUCCESS", "FAILED"):
            break
    return client.get_result(run_id)
