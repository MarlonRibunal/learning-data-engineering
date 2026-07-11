## Data-lake physics: partitioning and file layout

A Hive-style partition path (`.../year=2026/month=03/day=01/`) looks like a naming
convention, but it's really how a data lake gets *fast*. On object storage (S3,
GCS) there are no indexes — so **the directory layout *is* the index.**

- **Partition pruning.** A query filtered to March 1st reads only that folder and
  skips every other day's files. Choosing partition columns that match how data is
  filtered (usually date) is the single biggest query-performance lever on a lake.
- **The Goldilocks problem.** Partition too coarse (by year) and you scan too much;
  too fine (by hour, or by user_id) and you get the **small-files problem** —
  millions of tiny files whose per-file overhead destroys read performance. Aim for
  partitions holding reasonably large files.
- **File format matters as much as layout.** Columnar formats (**Parquet**, ORC)
  store data by column with built-in compression and stats, so engines skip whole
  row-groups — the file-level twin of partition pruning.
- **Table formats** (**Iceberg**, **Delta**, Hudi) add a metadata layer over the
  files, giving you ACID transactions, schema evolution, and hidden partitioning —
  the modern lakehouse.

Laying out files well is the unglamorous, high-leverage physics of cheap, fast
analytics at scale.

*Go deeper: partition pruning; the small-files problem; Parquet; Iceberg/Delta.*
