## Deadlines and the hung-job problem

A poll loop with no cap is a landmine: if the remote job hangs, your task hangs
with it — holding a worker slot, blocking downstream tasks, and never alerting.
Adding a **timeout** is how you defend against the failure mode monitoring misses,
because a hung job produces *no error* — just silence.

The concepts:

- **Deadlines / timeouts.** Every wait on something you don't control needs a
  bound. "Wait forever" is never a correct answer in distributed systems, where the
  network can drop a response and leave you waiting on a reply that will never come.
- **Fail fast on timeout.** Hitting the deadline should raise (a `TIMEOUT`), turning
  invisible hangs into visible failures you can retry or page on.
- **Poll interval trade-off.** Poll too often and you hammer the API (and your
  rate limit); too rarely and you add latency to detecting completion. Real clients
  often *back off* the poll interval over time.
- **Resource leaks.** A hung task doesn't just wait — it *holds* a worker. In a
  pool of N workers, a few hung tasks can starve the whole pipeline. Timeouts free
  the slot.

"Bound every wait" is a principle that shows up in HTTP clients, database queries,
lock acquisition, and orchestration alike.

*Go deeper: timeouts/deadlines; the hung-task resource leak; poll backoff.*
