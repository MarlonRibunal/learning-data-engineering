def backoff_delays(retries, base):
    return [base * (2 ** i) for i in range(retries)]
