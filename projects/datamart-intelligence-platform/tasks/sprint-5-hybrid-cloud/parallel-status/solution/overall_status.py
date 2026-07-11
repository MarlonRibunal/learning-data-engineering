def overall_status(statuses):
    if "FAILED" in statuses:
        return "FAILED"
    if "RUNNING" in statuses:
        return "RUNNING"
    return "SUCCESS"
