## Accepted values and enums

Some columns aren't free text — they're an **enumeration**: `status` is exactly
one of `shipped`, `pending`, `cancelled`. An **accepted-values** test guards that
set, and it catches a whole class of quiet corruption:

- a new code the upstream app started emitting that your logic doesn't handle
  (`refunded` appears, and your revenue rollup silently ignores it),
- a typo or casing drift (`Shipped`, `SHIPPED`, `shipped ` — three "different"
  statuses to a `GROUP BY`),
- a mapping bug that writes a raw integer where a label belongs.

The clean fix upstream is to **enforce the domain at write time** — a database
`CHECK` constraint or an `ENUM` type refuses the bad value entirely. But you often
don't control the source, so a downstream accepted-values test is your safety net.

This is really about **consistency**: the same concept represented the same way
everywhere. A dimension that drifts (three spellings of one status) fractures
every aggregate built on it. dbt ships `accepted_values` as a built-in for exactly
this reason.

*Go deeper: `CHECK` constraints / SQL enums; dbt `accepted_values`.*
