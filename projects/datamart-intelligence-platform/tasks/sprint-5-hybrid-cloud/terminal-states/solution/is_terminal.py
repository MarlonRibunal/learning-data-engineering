TERMINAL = {"SUCCESS", "FAILED", "CANCELED"}


def is_terminal(statuses):
    return [s in TERMINAL for s in statuses]
