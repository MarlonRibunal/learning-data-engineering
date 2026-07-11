## Averages lie (and how to slice safely)

Slicing a metric by a dimension — average order value *per status* — is the most
common serving shape, and the **average** is the most-misread statistic in
analytics. Serving it responsibly means knowing its traps.

- **The mean is not robust.** One $1,000,000 order drags "average order value" far
  from what a typical customer spends. The **median** (or a percentile like p90)
  often describes "typical" better; mature dashboards show both.
- **Simpson's paradox.** An average over a whole population can point the opposite
  way from the average within every subgroup. Slicing by the *right* dimension
  isn't cosmetic — it can flip the conclusion. This is exactly *why* you compute
  the metric *by status* rather than one blended number.
- **Weighting.** An average of per-group averages is **not** the overall average
  unless the groups are the same size — a subtle bug when you aggregate
  aggregates.

The engineering takeaway: a served metric carries assumptions (mean vs. median,
weighted vs. not, which slice), and encoding the *right* ones — consistently — is
what makes a dashboard trustworthy rather than merely populated.

*Go deeper: mean vs. median vs. percentiles; Simpson's paradox; weighted averages.*
