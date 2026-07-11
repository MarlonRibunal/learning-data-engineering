**Advanced challenges.** You've built the whole lifecycle. These are the harder
problems — the ones that separate someone who *uses* a data platform from
someone who could *build* one. Each is a small algorithm a real system runs
under the hood:

- **Blast radius** — traverse a dependency graph to find everything a failure
  breaks downstream.
- **Sessionization** — reconstruct user sessions from a raw event stream.
- **Retention curve** — the cohort analysis every growth team lives by.
- **Topological order** — the scheduling logic inside every orchestrator.

They're graph traversal, stateful iteration, and nested aggregation — the CS
fundamentals that show up constantly in data engineering interviews and
on-call. Take your time; these are meant to stretch you.
