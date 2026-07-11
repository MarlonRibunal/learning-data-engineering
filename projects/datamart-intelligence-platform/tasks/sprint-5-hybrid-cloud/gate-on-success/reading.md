## Barriers and all-or-nothing gates

"Proceed only if every upstream job succeeded" is a **barrier** (a join point): a
gate that downstream work can't cross until a whole set of prerequisites is
complete *and* healthy. It's the fan-in's decision made explicit.

Why the gate is strict:

- **Partial data is worse than no data.** Run the aggregation when only 3 of 5
  regional loads succeeded and you publish a total that's silently short — an
  error no one sees. The all-or-nothing gate refuses that.
- **Consistency boundary.** The barrier defines a point where you *know* a
  consistent set of inputs exists. Downstream can then assume completeness — an
  assumption worth enforcing rather than hoping for.
- **This is transactional thinking.** "All succeed or we don't proceed" is the
  atomicity of a transaction applied to a pipeline: the batch either fully lands or
  the step doesn't fire.

Orchestrators encode this with **trigger rules** — Airflow's default is
`all_success` (run only if *every* upstream succeeded), and it has variants
(`all_done`, `one_failed`) for when you want different gate semantics. Choosing the
right trigger rule is choosing how strict your barrier is.

*Go deeper: barriers/join points; Airflow trigger rules; atomicity in pipelines.*
