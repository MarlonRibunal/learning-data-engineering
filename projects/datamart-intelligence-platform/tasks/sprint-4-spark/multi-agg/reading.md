## One pass, many aggregates: Tungsten

Computing count, sum, and average in one `.agg(...)` isn't just tidy syntax — it's
also efficient, and *why* it's efficient is a window into how modern Spark runs.

All three aggregates share **one shuffle and one pass** over the grouped data.
Spark computes them together per group rather than scanning three times. Compare
the naive approach — three separate `groupBy` jobs — which would shuffle the data
three times over.

Under the hood, Spark's **Tungsten** execution engine makes each pass fast with
two techniques:

- **Whole-stage code generation** — instead of interpreting your operators row by
  row, Spark *compiles* a whole chain of them into tight JVM bytecode, collapsing
  many virtual calls into one loop.
- **Off-heap, cache-friendly memory** — Tungsten stores rows in compact binary
  format and operates on them directly, sidestepping JVM object overhead and
  garbage-collection pressure.

The takeaway: prefer **one wide operation that does many things** over many narrow
jobs that each re-shuffle. Batching aggregates into a single `.agg()` is a small
example of a big Spark principle — do the expensive movement once.

*Go deeper: Tungsten; whole-stage codegen; single-pass aggregation.*
