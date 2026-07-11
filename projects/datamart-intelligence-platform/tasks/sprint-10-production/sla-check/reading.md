## Meeting the promise: latency and the boundary

Checking whether a run met its latency target is an SLO evaluation in miniature,
and it surfaces two ideas that trip people up.

- **The boundary is a decision, not a detail.** Is *exactly* 200 ms a pass or a
  fail? "≤" vs "<" changes which runs breach. SLOs must define the comparison
  explicitly and apply it consistently, or your compliance number drifts with
  whoever wrote the check.
- **Latency is a distribution, not a number.** "Our latency is 120 ms" is
  meaningless without asking *which* latency. The **average** hides pain — a system
  can average 120 ms while 5% of requests take 2 seconds. That's why real SLOs are
  stated on **percentiles**: "p99 < 500 ms" means 99% of requests are under
  half a second. **Tail latency** (p95/p99) is what users actually feel, and it's
  usually what a data SLA is written against ("95% of the daily load finishes by
  6am").

So a single-run `actual ≤ target` check is the atom; the real practice is
evaluating a *distribution* of runs against a *percentile* target over a window,
with an unambiguous boundary. Freshness SLAs, query-latency SLOs, and
pipeline-completion promises are all this pattern scaled up.

*Go deeper: percentile/tail latency (p95/p99); why averages hide; SLO boundaries.*
