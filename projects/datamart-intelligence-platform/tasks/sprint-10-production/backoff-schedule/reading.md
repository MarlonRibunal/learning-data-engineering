## Backoff, jitter, and the thundering herd

Exponential backoff isn't just "wait longer each time" — it's a specific fix for a
specific distributed-systems failure, and the details matter.

- **Why exponential, not linear.** A struggling service needs *rapidly* decreasing
  pressure. Doubling the wait (1, 2, 4, 8…) backs off fast enough to let it
  recover, while capping total attempts.
- **The thundering herd.** Here's the subtle killer: if a shared dependency blips
  and *thousands* of clients all fail and all retry on the *same* backoff schedule,
  they retry in synchronized waves — hammering the recovering service at exactly
  the same moments and knocking it back down. Pure exponential backoff can turn one
  outage into a self-inflicted DDoS.
- **Add jitter.** The fix is **randomized backoff** — add (or fully randomize)
  jitter so retries spread out instead of synchronizing. AWS's "exponential backoff
  and jitter" is the canonical reference; "full jitter" often wins.
- **Cap it.** A maximum delay and a maximum attempt count keep backoff from waiting
  hours or retrying forever.

So a production retry policy is really *exponential backoff + jitter + caps* — the
schedule you built is the skeleton; jitter is what stops a fleet from
self-synchronizing into a second outage.

*Go deeper: exponential backoff with jitter (AWS Builders' Library); thundering
herd.*
