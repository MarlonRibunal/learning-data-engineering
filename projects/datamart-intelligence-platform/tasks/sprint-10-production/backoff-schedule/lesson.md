# Exponential backoff

Transient failures — a rate limit, a brief network blip — are normal in
distributed systems. Retrying **immediately and repeatedly** just makes it
worse (you hammer a struggling service). The fix is **exponential backoff**:
wait a little, then double the wait each attempt.

Delays of `base, base·2, base·4, base·8, …` give the downstream time to
recover while bounding total wait.

## Your task

Write `backoff_delays(retries, base)` returning the list of wait times for
`retries` attempts — starting at `base` and **doubling each time**:

```python
def backoff_delays(retries, base):
    return [base * (2 ** i) for i in range(retries)]
```

`backoff_delays(4, 1)` → `[1, 2, 4, 8]`.
