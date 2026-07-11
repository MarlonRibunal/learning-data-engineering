## Cohort analysis

The retention curve you built is the atom of **cohort analysis** — arguably the most
important lens in product analytics, because it answers the question that decides
whether a business compounds: *do the users we acquire stick around?*

- **A cohort** is a group bound by a shared start event — users who signed up in the
  same week, customers acquired in the same campaign. You then track *that fixed
  group* over time.
- **The retention curve** — how many of the cohort are still active on day 1, 7,
  30 — reveals product-market fit in a way top-line growth hides. Total users can
  rise while every cohort quietly churns (a "leaky bucket"): you're acquiring faster
  than you're losing, but the product isn't sticky. Cohorts expose that; aggregate
  metrics conceal it.
- **The full analysis** is a matrix — cohorts down the rows, age across the columns
  — read diagonally to compare cohorts at the same age. Whether newer cohorts retain
  *better* than older ones tells you if product changes are working.

The mechanic is a **set intersection per period** (cohort ∩ active-that-day), and
its cousins — funnel analysis, LTV, churn — are built from the same "track a fixed
group across stages/time" idea. Engineering these correctly (stable cohort
definitions, consistent activity events) is high-leverage analytics work.

*Go deeper: cohort/retention analysis; the retention matrix; funnels, churn, LTV.*
