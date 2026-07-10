def poll_result(statuses, max_polls):
    # TODO: return the FIRST terminal status (SUCCESS/FAILED/CANCELED) within
    # the first max_polls polls; return "TIMEOUT" if none finishes in time.
    return statuses[-1]
