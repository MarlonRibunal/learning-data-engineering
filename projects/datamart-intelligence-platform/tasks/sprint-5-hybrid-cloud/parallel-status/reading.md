## Fan-out, fan-in, and rolling up status

Kicking off several parallel jobs and rolling their statuses into one is the
**fan-out / fan-in** (scatter/gather) pattern — split work across workers, then
combine the results — and the "combine" step is subtler than it looks.

Aggregating distributed status is really about **precedence**: which outcome
dominates?

- **A failure dominates successes.** If any parallel job failed, the whole step
  failed, no matter how many succeeded — you can't proceed on partial data. Check
  the most severe state first (the bug you avoided).
- **"Still running" beats "all done."** The step isn't complete until *every*
  branch is terminal; one `RUNNING` means keep waiting.
- **This is a reduce.** You're folding many statuses into one with a
  precedence-ordered combine — the same shape as a distributed aggregation.

The pattern recurs all over data engineering: an Airflow task that waits on
several upstreams, a Spark stage that finishes only when all its tasks do, a
health check that's red if any dependency is red. Getting the precedence right —
and not letting one silent failure hide behind a wall of green — is what makes a
fan-in trustworthy.

*Go deeper: scatter/gather (fan-out/fan-in); status precedence; distributed reduce.*
