## Trust, but verify

The step everyone is tempted to skip: after the backfill runs without errors,
**prove the data is actually correct** before closing the incident. "The job
succeeded" and "the data is right" are different claims — a job can complete and
still write the wrong number of rows. Recovery isn't done when the pipeline is
green; it's done when the *numbers* reconcile.

The practices:

- **Reconciliation.** Compare actual row counts (or key metrics) against what you
  *expected* — source vs. target, before vs. after. A mismatch means the incident
  isn't over, however green the DAG looks. This is the same before/after check as a
  data migration.
- **Handle the missing case.** A table that vanished entirely is the *worst* case,
  not a null to crash on — verification must treat "absent" as "unrecovered."
- **Close the loop.** Verified recovery feeds the **post-mortem**: what broke, how
  we found it, how we fixed it, and — most importantly — what *systemic* change
  stops the whole class of failure from recurring.

"Trust, but verify" is the on-call maxim precisely because unverified recoveries
reopen the next morning as a stakeholder's angry message. The reconciliation is
what lets you say *done* and mean it.

*Go deeper: reconciliation checks; incident closure; blameless post-mortems &
follow-up actions.*
