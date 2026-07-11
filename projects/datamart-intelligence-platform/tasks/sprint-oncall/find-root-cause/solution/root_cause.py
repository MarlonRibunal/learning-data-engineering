def first_failure(runs):
    for run in runs:
        if run["status"] == "failed":
            return run["job"]
    return None
