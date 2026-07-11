## Dimensional modeling and the star schema

How you *shape* a warehouse is architecture, and the dominant pattern is Ralph
Kimball's **dimensional model** — the **star schema**. It splits the world into
two kinds of table:

- **Dimensions** — the *nouns*, the context: who, what, where, when. `dim_customers`
  is one row per customer with descriptive attributes (name, email, region).
  Dimensions are how humans *filter and group* ("revenue **by region**").
- **Facts** — the *verbs*, the measurements (next task): one row per business
  event, mostly numbers plus foreign keys to dimensions.

Draw it and a central fact table links out to surrounding dimensions like points
of a **star** — hence the name. It's deliberately *denormalized* compared to an
OLTP schema, because it's optimized for the two things analysts do: **slice**
(filter by a dimension) and **aggregate** (roll facts up).

A dimension's cardinal rule is **one row per business key** (one row per
customer) — its **grain**. Break that (duplicate customers) and every join to it
fans out and inflates your facts. Getting dimensions clean and unique is the
foundation everything else stands on.

*Go deeper: Kimball's "The Data Warehouse Toolkit"; star schema; dimensions vs.
facts.*
