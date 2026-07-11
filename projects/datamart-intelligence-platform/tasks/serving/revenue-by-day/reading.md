## Time series and the date spine

A "revenue per day" query looks simple, but time-series serving hides a classic
trap: **days with no data don't appear.** `GROUP BY order_date` only emits rows
for dates that *had* orders — so a zero-sales Sunday silently vanishes, and a line
chart draws a straight line across the gap as if nothing happened.

The fix is a **date spine** (a **date dimension**): a table with *one row per
calendar day*, which you `LEFT JOIN` your aggregates onto. Now every day exists,
missing days show a true `0`, and the chart tells the truth.

A proper date dimension earns its keep beyond gap-filling — it precomputes the
calendar attributes analysts constantly need: day-of-week, is-weekend, fiscal
quarter, holiday flags, week/month/quarter labels. Instead of deriving those in
every query, you join to one well-built table.

Time is the axis of almost every business question ("vs. last month", "trailing
7-day"), so a clean date dimension is one of the highest-leverage tables in a
warehouse — the backbone of trend, cohort, and seasonality analysis.

*Go deeper: date dimensions / date spines; `generate_series`; Kimball's calendar
dimension.*
