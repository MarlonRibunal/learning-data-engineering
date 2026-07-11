# Gate downstream on all successes

**The scenario.** The parallel jobs finished — now, should the *next* stage run?
Only if **every** upstream job succeeded. If even one failed, running downstream
would build on incomplete data. This all-or-nothing gate is what keeps a partial
failure from silently poisoning the rest of the pipeline.

## The task

`all(...)` over a generator is the clean way to say "every one of these is true":

```python
def all_succeeded(statuses):
    return all(s == "SUCCESS" for s in statuses)
```

`all_succeeded(["SUCCESS", "SUCCESS"])` → `True`. A single non-success flips it to
`False`, and the downstream stage should not run.

## Your task

Write `all_succeeded(statuses)` returning `True` only if every status is
`"SUCCESS"`.
