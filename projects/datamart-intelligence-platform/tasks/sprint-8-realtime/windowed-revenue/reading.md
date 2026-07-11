## Batch and streaming are the same thing

You wrote windowed revenue with the *exact* code you'd use on a batch — and that's
not a coincidence, it's the defining insight of modern data processing:
**a batch is just a bounded stream.**

Older architectures kept two totally separate systems: a batch pipeline for
accurate historical numbers and a streaming pipeline for fast approximate ones —
the **Lambda architecture** — which meant writing and maintaining the *same logic
twice*, in two languages, forever out of sync. Painful.

Frameworks like Spark Structured Streaming and Apache Flink collapsed that: one
API, one mental model, where a table is an ever-growing thing and a query over it
works whether the data is finished (batch) or still arriving (stream). Run it on a
file → batch. Point it at a stream → streaming. This is the **Kappa
architecture** — one codebase for both.

So the reason your batch windowing "just works" on a stream is deliberate design.
Learn the windowing logic once, apply it to bounded or unbounded data. That
unification is why the streaming and batch sprints in this course share so much
code.

*Go deeper: Lambda vs. Kappa architecture; the "streaming is a superset of batch"
model.*
