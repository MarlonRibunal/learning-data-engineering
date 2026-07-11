## Event time vs. processing time

The single most important idea in stream processing: there are **two clocks**.

- **Event time** — when the thing actually happened (the timestamp *in* the
  event: when the order was placed).
- **Processing time** — when your system got around to handling it.

They differ, often wildly: a mobile app buffers events offline and uploads a batch
hours later; a network retry delays a message. If you window by *processing* time,
that late order lands in the wrong bucket and your "9:00–9:10 revenue" is wrong.
Windowing by **event time** — grouping on the event's own timestamp, as you did
with `window("ts", ...)` — puts every event in the bucket it belongs to, no matter
when it arrived.

Choosing event time is what makes streaming results *correct* rather than merely
*fast*, and it's the reason streaming frameworks obsess over timestamps and
watermarks. Batch processing quietly gets event-time correctness for free (all the
data is already there); streaming has to work for it — which is the whole plot of
the next few levels.

*Go deeper: event time vs. processing time; "The Dataflow Model" (Google).*
