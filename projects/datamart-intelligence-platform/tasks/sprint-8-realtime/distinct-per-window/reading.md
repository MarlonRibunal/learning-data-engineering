## Bounded vs. unbounded state

Counting *distinct* values per window exposes streaming's hardest constraint:
some computations need **unbounded state**. To count distinct categories exactly,
you must *remember every distinct value seen* in the window — and on a real stream
with millions of distinct users, that memory grows without limit.

Streaming's answer is to trade exactness for bounded memory:

- **Approximate algorithms.** `approx_count_distinct` uses **HyperLogLog**, a
  probabilistic *sketch* that estimates cardinality in a few kilobytes regardless
  of how many distinct values pass through — ~2% error for a massive memory win.
  Related sketches: **Bloom filters** (set membership), **Count-Min** (frequencies),
  **t-digest** (percentiles).
- **Watermarks + windows** bound state the other way — by *time*: once a window is
  finalized and its watermark passes, its state is dropped.

The mindset shift from batch is real: in batch you compute the exact answer over
finite data; in streaming you constantly ask *"can this be done in bounded state,
and if not, is an approximation good enough?"* For "how many unique users this
minute," a 2%-accurate answer *now* usually beats an exact answer that needs
infinite RAM.

*Go deeper: HyperLogLog & sketch algorithms; bounded-state streaming.*
