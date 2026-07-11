# Sessionize an event stream

**The scenario.** Raw events are just timestamps. A "session" is a burst of
activity with quiet gaps between — a browsing visit, a work session. Turning a
flat stream into sessions (**sessionization**) is a bread-and-butter data-eng
task, and the logic is a **stateful pass**: walk the sorted times, and start a
new session whenever the gap since the last event exceeds a threshold.

## The pass

```python
def count_sessions(times, gap):
    if not times:
        return 0
    times = sorted(times)
    sessions = 1
    for prev, curr in zip(times, times[1:]):
        if curr - prev > gap:
            sessions += 1
    return sessions
```

- **Sort first** — sessions are defined over time order.
- **Compare consecutive pairs** — `zip(times, times[1:])` is the clean idiom for
  "each element and the next."
- A gap **strictly greater** than the threshold breaks the session. (You did the
  windowed version of this in Spark with `session_window`; here's the logic
  itself.)

## Your task

Write `count_sessions(times, gap)` returning the number of sessions. With times
`[0, 3, 7, 20, 22]` and a gap of `5`: the jump from 7 to 20 (13 > 5) splits it
into **2** sessions.
