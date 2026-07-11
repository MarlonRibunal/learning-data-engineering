## Deltas, context, and how percentages deceive

A percentage change is the smallest unit of *context* — and one of the easiest
numbers to misread, which makes computing it correctly a real responsibility.

- **The base matters.** % change divides by the *previous* value; get the base
  wrong and the number inverts. And a huge % on a tiny base is noise dressed as
  news ("+300%!" from 1 to 4).
- **Percentages don't add or average.** A +50% followed by −50% is not 0% — it's
  −25%. Chaining or averaging percent changes without going back to absolutes is a
  classic reporting bug.
- **Point-to-point is fragile.** Comparing today to yesterday swings on noise and
  seasonality (Monday vs. Sunday). That's why real dashboards prefer
  **period-over-period on comparable periods** (this week vs. same week last year)
  or a smoothed trend — connecting to the moving-average level.
- **Guard the divide-by-zero.** No prior value means the % is undefined, not
  infinite; handle it explicitly.

The tiny "▲ 12%" is the most decision-driving element on a dashboard, so the
engineer's job is to make sure it's computed on the right base, over comparable
periods, and honest about small numbers.

*Go deeper: relative vs. absolute change; base-rate traps; seasonality &
comparable periods.*
