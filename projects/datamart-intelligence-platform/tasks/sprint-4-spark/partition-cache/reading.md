## Partitions, caching, and lineage

Two levers you pulled in this task control Spark's two scarcest resources —
parallelism and memory.

**Partitions** are the unit of parallelism. A DataFrame is split into partitions,
and Spark runs one **task** per partition per core. Too few partitions and cores
sit idle; too many and scheduling overhead dominates. `repartition(n)` (a full
shuffle) and its cheaper cousin `coalesce(n)` (merge without shuffle) tune this.
The rule of thumb: enough partitions to keep every core busy, not so many that
tasks become tiny.

**Caching** exploits Spark's **lineage**. Because transformations are lazy, a
DataFrame is really a *recipe* to recompute from its source — and by default Spark
*re-runs that recipe every time you branch off it*. If you use a DataFrame
multiple times (an ML loop, several downstream aggregates), `.cache()` /
`.persist()` materializes it in memory (or spilling to disk) so it's computed
once, not N times.

Lineage is also **fault tolerance**: if a machine dies, Spark just recomputes that
partition's recipe — no replication needed. Partitions, caching, and lineage
together are why Spark is both fast and resilient.

*Go deeper: partitions vs. tasks; `repartition`/`coalesce`; `cache`/`persist`;
RDD lineage.*
