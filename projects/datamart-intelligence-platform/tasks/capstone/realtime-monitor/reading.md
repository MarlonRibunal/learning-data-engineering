## A streaming pipeline, end to end

Where the batch capstone assembles the *batch* lifecycle, this one assembles the
*streaming* one into a single deliverable: raw events → **clean** → **window** →
**alert** — the shape of every real-time analytics system, from live dashboards to
fraud detection.

The architecture it distills:

- **Ingest & clean at the edge.** Streams carry junk; the first stage filters and
  validates *before* aggregation, so bad data never enters the windows. Quality
  isn't a later stage — on a stream it has to be first.
- **Window over event time.** The core transform aggregates by event-time windows —
  the batch/streaming-unified logic you've built repeatedly, now as the beating
  heart of the pipeline.
- **Derive a signal.** The busiest-window "alert" turns a metric into a *decision* —
  the same metric→signal step as a dashboard threshold, which is what makes a
  monitor actionable rather than merely informative.

Building it as three composed functions mirrors how real streaming jobs are
structured — a chain of transformations on an unbounded table — and reinforces that
streaming reuses the exact concepts (event time, windows, watermarks, quality)
you'd apply in batch. A working real-time pipeline you can demonstrate is a
standout portfolio piece precisely because streaming is where many engineers stall.

Two capstones, two halves of the craft: **batch** (accurate history) and
**streaming** (fast present) — and you've now built both, end to end.

*Go deeper: streaming pipeline architecture; the clean→window→serve pattern;
Lambda/Kappa revisited.*
