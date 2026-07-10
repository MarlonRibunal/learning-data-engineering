# Session windows

**The scenario.** Tumbling and sliding windows are fixed to the clock. But
"a user's browsing session" isn't — it lasts as long as they keep clicking, and
ends when they go quiet. A **session window** is defined by **inactivity**: keep
one window open while events keep arriving within a gap, and start a new one
after a quiet stretch. It's how you measure sessions, visits, and bursts.

## The idea

Instead of a fixed size, you give a **gap duration**. Events closer together
than the gap belong to the same session; a gap larger than that starts a new
one:

```python
from pyspark.sql import functions as F

events \
    .withColumn("ts", F.to_timestamp("ts")) \
    .groupBy(F.session_window("ts", "5 minutes")) \
    .count()
```

With a 5-minute gap and events at 09:03, 09:07, 09:12, then 09:18, then 09:25:
the first three are each within 5 minutes of the next, so they form **one**
session (09:03–09:12, count 3). The 6-minute gap to 09:18 breaks it; 09:18 and
09:25 each start their own. `session_window` produces a struct with `.start` and
`.end`, just like `window`.

## Your task

Write `transform(events)` returning **`session_start`** (the session's start as
a string, from `session_window.start`) and **`count`** of events per session,
using a **5-minute** inactivity gap.
