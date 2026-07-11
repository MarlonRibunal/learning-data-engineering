## Jobs are state machines

Splitting statuses into "still going" and "finished" is really recognizing that a
job is a **finite state machine**: it moves through a defined set of states along
allowed transitions, and some states are **terminal** (no transitions out).

`PENDING → RUNNING → SUCCESS` (terminal), or `RUNNING → FAILED` / `CANCELED` (also
terminal). Modeling it explicitly pays off:

- **Terminal detection drives the loop.** "Keep polling until terminal" only works
  if you've correctly classified which states are ends. Miss that `CANCELED` is
  terminal and your loop polls a dead job forever.
- **Illegal transitions are bugs.** A job shouldn't go `SUCCESS → RUNNING`; if your
  code sees that, something's wrong (a stale read, a reused id).
- **Vocabularies differ, the shape doesn't.** Databricks, Kubernetes, Airflow, and
  Step Functions each name states differently, but all split into in-flight vs.
  terminal, and terminal into success vs. failure. Map any new API onto that shape.

State machines are everywhere in data engineering — task lifecycles, order
fulfillment, SCD validity, workflow engines. Seeing "what are the states and which
are terminal?" is a reusable lens.

*Go deeper: finite state machines; job lifecycle modeling; state diagrams.*
