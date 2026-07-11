**On-call incident: the dashboard is stale.** It's 2am. PagerDuty fires: the
executive dashboard hasn't updated since yesterday. You're on call. This isn't a
single skill — it's the whole loop a data engineer runs during an incident:

1. **Triage** — which tables are actually breached? Don't chase noise.
2. **Find the root cause** — one failed upstream job usually broke everything
   downstream; find *that* one, not its victims.
3. **Backfill** — recompute exactly the missing window, no gaps, no overlaps.
4. **Verify recovery** — prove the numbers are right again before you go back to
   bed.

Each level is one step of that incident. Together they're the muscle memory that
turns a 2am page from panic into procedure.
