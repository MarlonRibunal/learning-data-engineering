## From metric to signal

Turning a value into ok/warn/critical is the moment a dashboard stops *reporting*
and starts *alerting* — and the design of that threshold logic is where analytics
meets operations.

The ideas that make status signals useful rather than annoying:

- **Thresholds encode a decision.** Green/amber/red is a policy: "below 80 is fine,
  80–95 watch, above 95 act." Choosing those cut points *is* the work — too tight
  and you drown in false alarms (alert fatigue → people ignore real ones); too
  loose and you miss incidents.
- **Order of checks matters.** Test the most severe band first, or a critical value
  matches "warn" on the way down — the bug you avoided in the task.
- **Hysteresis avoids flapping.** A value hovering at the boundary shouldn't
  toggle red/green every refresh; real alerting adds a buffer or a "must stay over
  for N minutes" rule so status is stable.
- **Static thresholds vs. anomaly detection.** Fixed cut-points are simple but
  blind to seasonality; mature monitoring learns a normal *band* and flags
  deviations from it.

This is the UX of on-call: a good status tile turns a stream of numbers into a
clear "do I need to do something?" — which is the whole point of a dashboard that
runs a business.

*Go deeper: alert thresholds & fatigue; hysteresis; static vs. anomaly-based
alerting.*
