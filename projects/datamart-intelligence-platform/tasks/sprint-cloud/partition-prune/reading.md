## Partitioning and clustering on the cloud

Partition pruning is the query engine's first line of "read less," and cloud
warehouses give you two complementary knobs to make it effective.

- **Partitioning** splits a table into segments by a column — almost always a
  **date** (daily partitions). A filtered query prunes whole partitions before
  reading. But partition on the wrong column (or too finely) and you get the
  same **small-files / too-many-partitions** problem as a data lake. Date is
  usually right because most analytics is time-bounded.
- **Clustering** (BigQuery) / **Z-ordering** (Delta) sorts data *within*
  partitions by frequently-filtered columns, so the engine skips blocks inside a
  partition too — a second layer of pruning for the columns you filter on after
  date.

Under both is the same physics you met with Parquet and data-lake paths:
columnar storage keeps per-block **min/max statistics**, so the engine can prove
a block can't contain matching rows and skip it unread. Partitioning, clustering,
and column pruning are all ways of helping that proof succeed more often.

Designing the partition/cluster keys to match your query patterns is one of the
highest-leverage — and most cost-saving — decisions on any cloud warehouse.

*Go deeper: BigQuery partitioning & clustering; Delta Z-ordering; min/max block
pruning.*
