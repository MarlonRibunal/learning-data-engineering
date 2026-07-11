## Least privilege and RBAC

Security's foundational principle is **least privilege**: every person and process
gets the *minimum* access needed to do its job — no more. An analyst who only
reads should be *unable* to write, so a bug, a bad query, or a compromised
credential can't corrupt or delete data. You're not distrusting the analyst;
you're limiting the *blast radius* of any mistake.

Databases implement this with **RBAC** (Role-Based Access Control):

- **Roles**, not people, hold privileges (`GRANT SELECT ... TO analyst`). Humans
  and services are *granted the role*, so access is managed in one place.
- Privileges are **granular** — `SELECT` vs `INSERT`/`UPDATE`/`DELETE`, per table,
  even per column.
- Access is **layered**: `USAGE` on the schema *and* `SELECT` on the table — miss
  either and the role can't read.

This is an **undercurrent** of the whole lifecycle (from *Fundamentals of Data
Engineering*): security isn't a stage you do at the end, it's a property every
stage must uphold. A read-only role is the simplest expression of "give exactly
enough, and no more."

*Go deeper: least privilege; RBAC; the principle of defense in depth.*
