### Fan out: run tasks in parallel

Not every step is sequential. Often one task kicks off several that can run at the same
time. In Airflow you express that with a **list** on the right of `>>`.

**Your task:** make `left` and `right` both run **after** `start`, in parallel.

```
start_task >> [left_task, right_task]
```

Airflow schedules `left` and `right` together once `start` finishes. Fan-out (and its
mirror, fan-in) is how real DAGs get wide and fast.

> Needs the stack: `./platform.sh up` first.
