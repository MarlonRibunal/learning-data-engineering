## Time travel and the immutable log

Time travel falls out *for free* from how the lakehouse stores data: because the
transaction log records **every commit** and data files are **immutable** (a
change adds new files, it doesn't overwrite old ones), the old versions are still
sitting there. Point at an earlier log state and you reconstruct the table as it
was.

What it unlocks in practice:

- **Audit & reproducibility** — "what did this table look like when we ran that
  report?" Re-run against `VERSION AS OF` and get the exact same numbers.
- **Debugging** — a bad load corrupted a table? Diff the current version against
  the prior one to see precisely what changed.
- **Rollback** — restore a table to a known-good version in one command, instead
  of a frantic backfill.
- **Reproducible ML** — train against a pinned data version so an experiment is
  repeatable.

This is the *automatic* version of the snapshot tables you built by hand in
Architecture — the log gives you every version without you maintaining anything.
The trade-off is storage (old files are retained until a **vacuum**/retention
policy cleans them), and the discipline of setting sensible retention.

The theme across this whole sprint: the log-and-immutability design that makes a
lakehouse work is the same idea behind Kafka's log, event sourcing, and git —
**an append-only history is a superpower.**

*Go deeper: Delta time travel & VACUUM; data versioning for ML; log-structured
storage.*
