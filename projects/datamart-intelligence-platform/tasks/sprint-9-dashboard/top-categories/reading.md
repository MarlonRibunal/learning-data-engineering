## Ranking honestly

A top-N bar chart is where dashboards most often mislead — usually by accident.
Getting it right is as much ethics as engineering.

- **Sort and cut deliberately.** "Top categories" means sorted *descending* and
  limited — but silently dropping the tail can distort the story. If the top 5 are
  15% of revenue, a chart implying they're "the business" lies. An **"Other"**
  bucket keeps the whole visible and the totals honest.
- **Truncated axes exaggerate.** A bar chart whose y-axis starts at 90 instead of 0
  turns a 2% difference into a visual landslide. Bars encode length, so their axis
  must start at zero — one of the oldest rules in data viz, and one of the
  most-broken.
- **Rank by the metric that matters.** By revenue, whales dominate; by order count,
  cheap items win. The "top" list changes entirely with the measure — so pick the
  one that fits the decision, and label it.

Edward Tufte's idea of **graphical integrity** — the visual should be proportional
to the numbers — is the standard here. As the engineer feeding the chart, you
choose the sort, the cutoff, and the bucketing that keep it honest.

*Go deeper: Tufte's graphical integrity; the "Other" bucket; zero-baseline bars.*
