# Which run states are terminal?

**The scenario.** Your poll loop (two levels back) asks "is the run finished
yet?" To answer, it has to know which states mean **done** and which mean **keep
waiting**. Every job API has its own vocabulary, but they all split into two
buckets:

- **In-flight** (keep polling): `PENDING`, `RUNNING`, `QUEUED`, …
- **Terminal** (stop polling): `SUCCESS`, `FAILED`, `CANCELED`.

Getting this wrong is a classic bug: treat `PENDING` as terminal and you'll act
on a job that hasn't started; forget that `CANCELED` is terminal and your loop
polls forever.

## Your task

Write `is_terminal(statuses)` returning a list of booleans — `True` where the
status means the run has finished:

```python
TERMINAL = {"SUCCESS", "FAILED", "CANCELED"}

def is_terminal(statuses):
    return [s in TERMINAL for s in statuses]
```

`is_terminal(["PENDING", "RUNNING", "SUCCESS", "FAILED"])` →
`[False, False, True, True]`. A `set` membership test is both the clearest and
the fastest way to express "is this one of the finished states."
