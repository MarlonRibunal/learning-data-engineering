def all_succeeded(statuses):
    return all(s == "SUCCESS" for s in statuses)
