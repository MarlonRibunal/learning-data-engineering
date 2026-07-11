## Resilience patterns

A circuit breaker — trip open after N consecutive failures so you stop hammering a
dead dependency — is one of a small family of **resilience patterns** that keep a
failure in one component from cascading into a system-wide outage.

- **Circuit breaker.** Three states: *closed* (normal), *open* (failing fast
  without even trying, giving the dependency room to recover), and *half-open*
  (tentatively testing if it's back). It converts slow, piling-up timeouts into
  instant, cheap failures — and crucially, it *stops adding load to something
  that's already down*, which is often what turns a blip into an outage.
- **Bulkhead.** Isolate resources (separate connection pools/thread pools per
  dependency) so one slow dependency can't exhaust the resources the rest need — the
  ship's-hull metaphor: one flooded compartment doesn't sink the vessel.
- **Timeout + retry + backoff** — the trio from earlier levels, the first line of
  defense the breaker backstops.
- **Graceful degradation.** When a dependency is down, serve stale/cached/partial
  data instead of failing the whole request.

Together these encode a production mindset: **failure is inevitable, so design so
that a component failing degrades the system instead of collapsing it.** The
circuit breaker's specific job is halting the cascade.

*Go deeper: circuit breaker (Nygard's "Release It!"); bulkhead; graceful
degradation.*
