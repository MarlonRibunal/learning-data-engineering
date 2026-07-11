## Schema evolution and the expand-contract migration

An upstream column rename is a **schema evolution** event, and how you absorb it
separates fragile pipelines from robust ones. The naive move — rename everywhere at
once — breaks every consumer the instant it lands. The professional move is a
**backward-compatible, staged migration**.

The canonical pattern is **expand-contract** (a.k.a. parallel change):

1. **Expand** — add the new shape *alongside* the old (map old→new, or write both).
   Nothing breaks; old and new coexist.
2. **Migrate** — move consumers to the new shape one at a time, at their own pace.
3. **Contract** — once nothing reads the old shape, remove it.

The mapping step you built (`old_name → new_name`) is the *expand* phase: a
translation layer that lets old data flow into the new schema without a hard
cutover. Related tools:

- **Schema registries** (Avro/Protobuf) enforce compatibility rules so a producer
  *can't* ship a breaking change unnoticed.
- **Views as an abstraction** — expose a stable view name over a changing table so
  consumers are insulated from physical renames.

Schemas are contracts between teams, and evolving a contract without a flag day is a
core data-platform skill. Expand-contract is how you change the wheels while the car
keeps driving.

*Go deeper: expand-contract / parallel-change migrations; schema registries;
backward compatibility.*
