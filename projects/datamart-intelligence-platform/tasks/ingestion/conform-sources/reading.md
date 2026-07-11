## Conforming: one truth from many sources

Every company of any size has the same order, the same customer, the same
"revenue" living in three systems that each spell it differently — web vs. store,
Stripe vs. PayPal, the CRM vs. the billing DB. **Conforming** is the work of
reshaping those into one shared definition so they can be analyzed together.

Two ideas from data modeling underpin it:

- **Conformed dimensions** (Kimball's term) — a customer or a date means the
  *same thing* across every fact table, so metrics are comparable. Getting there
  means mapping each source's columns onto a canonical schema (the store's
  `total` becomes the shared `amount`).
- **Lineage / provenance** — stamping a `source` column so you never lose *where*
  a row came from. When the numbers look wrong, "which channel?" is the first
  question, and a source tag answers it instantly.

This is **data integration**, and it's deceptively hard: the SQL (`UNION ALL`) is
trivial, but agreeing on *what a customer is* across teams is an
organizational problem as much as a technical one. The conformed layer is where
that agreement gets encoded.

*Go deeper: Kimball conformed dimensions; the "single source of truth" ideal.*
