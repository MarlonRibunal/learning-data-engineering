## The dimensions of data quality

"Is this data good?" is too vague to test. The discipline breaks quality into
**dimensions**, each independently checkable:

- **Validity** — values obey their rules (an amount ≥ 0, a date in range).
- **Completeness** — required fields aren't missing.
- **Uniqueness** — no unintended duplicates.
- **Consistency / referential integrity** — values agree across tables.
- **Accuracy** — values match reality (hardest to test automatically).
- **Timeliness / freshness** — data is recent enough to trust.

This task is a **validity** (range) check. Its deeper lesson is *where* to test:
push checks as far **upstream** as you can. Catch a negative amount at ingestion
and one row is quarantined; let it flow to a mart and it silently skews every
revenue report downstream of it — the **1×10×100 rule** (a defect costs 1 to fix
at the source, 10 downstream, 100 once a stakeholder acts on it).

A test that returns the *violating rows* (zero = healthy) is the universal shape,
because it doubles as both an alarm and a work-list of exactly what to fix.

*Go deeper: data-quality dimensions; dbt tests / Great Expectations.*
