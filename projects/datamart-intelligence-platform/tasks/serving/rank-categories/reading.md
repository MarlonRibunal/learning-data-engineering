## Top-N, cardinality, and honest ranking

"Top categories" is a **top-N** query, and serving them well is more subtle than
`ORDER BY ... LIMIT`.

- **Cardinality matters.** Ranking 8 categories is trivial; ranking millions of
  products means the "long tail" dwarfs the head. Dashboards almost always show
  "top N + an *Other* bucket" so the chart stays readable and the totals still
  add up — dropping the tail entirely would make the numbers lie.
- **Ties need a rule.** `RANK` leaves gaps (1,2,2,4), `DENSE_RANK` doesn't
  (1,2,2,3), `ROW_NUMBER` forces a winner. "Top 3" is ambiguous when #3 and #4
  tie — decide deliberately, or your "top 3" silently drops a legitimate tie.
- **Per-group top-N** ("top 3 products *in each* category") is the real workhorse,
  and it needs `ROW_NUMBER() OVER (PARTITION BY ...)` — a window, not a global
  `LIMIT`.

Ranking also invites **metric mischief**: rank by revenue and a few whales
dominate; rank by count and cheap items win. The "right" ranking depends on the
decision it feeds — a reminder that a served number is only as good as the
question it's meant to answer.

*Go deeper: top-N-per-group with `ROW_NUMBER`; the "Other" bucket; RANK variants.*
