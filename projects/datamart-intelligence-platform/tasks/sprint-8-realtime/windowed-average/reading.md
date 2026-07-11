## Incremental aggregation

A streaming average updates continuously as events arrive — which raises a
question batch never has to: how do you keep an average *up to date* without
re-reading all the events each time?

The answer is **incremental (associative) aggregation**. The engine doesn't store
every value and recompute; it keeps a small **partial state** and folds each new
event in. For an average, that state is `(running_sum, running_count)` — a new
event adds to both, and the average is derived on demand. Bounded state, O(1)
update per event.

This is why some aggregates stream cleanly and others don't:

- **Easy** — sum, count, min, max, average: all *incremental*. You can merge two
  partial states (associativity), which also lets the engine parallelize and
  combine across partitions.
- **Hard** — exact median/percentiles: not incrementally mergeable without keeping
  all values, so streaming reaches for approximate sketches (t-digest) instead.

Whether a metric can be computed as a mergeable partial aggregate decides whether
it streams in bounded memory. It's the same property that makes distributed
`reduce` work — and recognizing it is what lets you tell, up front, which metrics
are cheap to stream.

*Go deeper: associative/incremental aggregation; partial aggregates; why median
is hard to stream.*
