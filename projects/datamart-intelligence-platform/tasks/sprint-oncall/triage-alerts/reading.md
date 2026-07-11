## Triage and the economics of attention

The first skill of on-call isn't fixing — it's **triage**: deciding what deserves
your attention *right now* and what doesn't. During an incident, attention is the
scarcest resource, and spending it on noise is how small problems become big ones.

- **Severity, not volume.** Ten alerts firing doesn't mean ten problems — often one
  root cause lights up ten downstream checks. Triage means finding the *few that
  matter*, not reacting to the count.
- **Alert fatigue is the real enemy.** A monitoring system that cries wolf trains
  people to ignore it — and the one real alert drowns in the noise. Good alerting is
  *high signal*: page on user-impacting symptoms (the dashboard is stale), not on
  every internal wobble.
- **Symptom vs. cause.** Alert on **symptoms** users feel (SLO breaches), then
  *diagnose* toward causes. Alerting on every possible cause creates the noise;
  alerting on symptoms keeps the page list short and meaningful.

Sorting breached-from-fine is the entry point to **incident management**: assess
impact, set severity, then act. A tidy, sorted list of what's actually broken is
the calm first move that makes the rest of the incident tractable.

*Go deeper: incident triage & severity; alert fatigue; symptom-based alerting.*
