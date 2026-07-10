**Unified dashboards.** At the end of the pipeline, someone actually *looks* at the data — a KPI tile, a trend line, a top-N bar chart. This platform's own UI is a Streamlit dashboard; so are most internal analytics tools data engineers ship.

A dashboard is only as trustworthy as the **data functions** behind each chart. The chart library is easy; getting the numbers right — the rollups, the ordering, the top-N — is the engineering. So that's what you'll build here: the pure functions that turn raw rows into exactly the shape a KPI card, a line chart, or a bar chart needs.

Each task gives you a list of order rows and asks for a function returning chart-ready data. No plotting to grade — just the data, which is the part that has to be correct.

> These are plain Python (no Spark, no database), so feedback is instant.
