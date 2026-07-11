## Plausibility: valid but wrong

The trickiest bad data isn't malformed — it's **well-formed and impossible**. A
date of `2099-01-01` is a perfectly valid `DATE`; it passes type checks, isn't
null, isn't a duplicate. Only a **plausibility** (range/sanity) check — does this
value make sense for *this* column — catches it.

Where impossible-but-valid values come from:

- **Sentinels leaking through** — `9999-12-31` or `1970-01-01` (the Unix epoch)
  used as "no date," accidentally treated as a real one.
- **Unit / timezone bugs** — milliseconds parsed as seconds, a date shifted a day
  by a timezone slip.
- **Fat-fingered input** — a human typed the year wrong.

The damage is disproportionate: one far-future date stretches a time-series
x-axis to the year 2099 and wrecks "revenue this month" math, all from a single
row. This is why anomaly and **distribution** monitoring (is today's row count,
min, max, or null-rate wildly off yesterday's?) is the frontier of data quality —
tools like Great Expectations and Monte Carlo watch the *shape* of data, not just
individual rules.

*Go deeper: range/anomaly checks; data observability (Great Expectations, Monte
Carlo).*
