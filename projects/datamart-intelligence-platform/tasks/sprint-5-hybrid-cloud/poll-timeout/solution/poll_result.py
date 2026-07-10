TERMINAL = {"SUCCESS", "FAILED", "CANCELED"}


def poll_result(statuses, max_polls):
    for i, status in enumerate(statuses):
        if i >= max_polls:
            break
        if status in TERMINAL:
            return status
    return "TIMEOUT"
