# Which errors to retry

**The scenario.** Your pipeline calls an API and gets an error. Backing off and
retrying (the previous level) only helps for the *right kind* of error. Retry a
**transient** failure (the service is briefly overloaded) and it'll probably
work next time. Retry a **permanent** one (you sent a malformed request) and
you'll just fail slower — three times — before giving up. Knowing the difference
is the difference between a resilient pipeline and a stubborn one.

## The rule of thumb (HTTP)

- **Retryable** (transient): `429` too many requests, `500` `502` `503` `504`
  server/gateway errors. The request was fine; the service wasn't ready.
- **Not retryable** (permanent): `4xx` client errors like `400` bad request,
  `401` unauthorized, `404` not found. Retrying won't change the outcome — fix
  the request instead.

## Your task

Write `retry_plan(status_codes)` that returns a list of booleans — `True` where
the code is worth retrying, `False` where it isn't:

```python
RETRYABLE = {429, 500, 502, 503, 504}

def retry_plan(status_codes):
    return [code in RETRYABLE for code in status_codes]
```

`retry_plan([503, 400, 429])` → `[True, False, True]` — retry the overload and
the rate-limit, give up on the bad request.
