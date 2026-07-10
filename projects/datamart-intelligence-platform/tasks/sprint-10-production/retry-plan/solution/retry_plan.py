RETRYABLE = {429, 500, 502, 503, 504}


def retry_plan(status_codes):
    return [code in RETRYABLE for code in status_codes]
