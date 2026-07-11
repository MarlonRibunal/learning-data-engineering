## The data behind the pixels

A KPI card is the simplest visualization — a single number — and a useful reminder
that **data engineering owns the number, not the chart.** The card's job is to
turn a rollup into an at-a-glance answer, and doing it well is mostly about *what*
the number is, not how it's drawn.

Principles that make a single-value display trustworthy:

- **A number needs context.** "$170k" alone is inert. The good version pairs it
  with a comparison (vs. last period), a target, or a trend — which is why the next
  levels build % change, sparklines, and thresholds. A KPI without context can't
  drive a decision.
- **Define it once, precisely.** "Total revenue" must mean the same thing here as
  in every other tile — the semantic-layer point from the serving sprint. A card is
  only as trustworthy as the definition behind it.
- **Round for humans.** `avg_order_value = 34.0`, not `33.9999`. Presentation
  rounding is a data-quality courtesy.

The BAN ("big-ass number") is the most-viewed element on any dashboard precisely
because it's simple — so the engineering rigor goes into the value, not the visual.

*Go deeper: KPI/BAN design; the semantic layer; "a number needs a comparison."*
