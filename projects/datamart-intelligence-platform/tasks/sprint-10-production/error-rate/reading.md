## SLIs, SLOs, and error budgets

An error *rate* is more than a number — it's the raw material of how modern
operations (SRE) decide whether a system is healthy *enough*, using a precise
vocabulary.

- **SLI (Service Level Indicator)** — a measured quantity: the error rate,
  latency, availability. Your `error_rate` is an SLI.
- **SLO (Service Level Objective)** — the *target* for an SLI: "error rate < 1%",
  "99.9% of loads succeed." The line between acceptable and not.
- **SLA (Service Level Agreement)** — an SLO with *consequences* — a contractual
  promise to a customer, with penalties if broken.

The powerful idea layered on top is the **error budget**: if your SLO is 99.9%
success, you have a 0.1% *budget* to spend on failures. That reframes reliability
from "zero errors" (impossible, and paralyzing) to "stay within budget." Spend the
budget → freeze risky changes and stabilize. Budget to spare → ship faster. It
turns an emotional argument ("is this reliable enough?") into an accounting one.

This is why a rate beats a raw count: you compare a *rate* against an SLO, and
track cumulative failures against a *budget*. Alerting thresholds are really "am I
burning my error budget too fast?"

*Go deeper: SLI/SLO/SLA; error budgets; Google's SRE book.*
