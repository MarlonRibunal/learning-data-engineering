## Narrow vs. wide: the cost of a shuffle

Not all Spark operations cost the same. The dividing line is whether data has to
move between machines.

- **Narrow transformations** (`select`, `filter`, `withColumn`) — each output
  partition depends on one input partition. No data crosses the network; blazing
  fast, fully parallel.
- **Wide transformations** (`groupBy`, `join`, `distinct`, `repartition`) — output
  partitions depend on *many* input partitions, so Spark must **shuffle**:
  repartition and send rows across the cluster so all rows for a key land
  together.

A `groupBy` is a wide transformation, and the shuffle it triggers is usually the
**most expensive thing in a Spark job** — it writes intermediate data to disk and
moves it over the network. This is why "how many shuffles does my job do?" is the
first performance question a Spark engineer asks, and why the optimizer works so
hard to combine narrow steps and minimize wide ones.

Understanding narrow vs. wide turns Spark from a black box into something you can
reason about: the fast parts stay on each machine; the slow parts move data.

*Go deeper: shuffles; narrow vs. wide dependencies; stages in the Spark DAG.*
