## Why data is split across tables (and joins put it back)

You might wonder why the customer's name isn't just stored on every order. The
answer is **normalization**: store each fact *once*, in one place. The customer's
name lives in `customers`; orders reference it by `customer_id`. If a customer
renames, you update one row, not thousands. Normalization removes redundancy and
the update anomalies it causes — a foundational idea of relational databases.

The cost of that tidiness is that answering real questions means **rejoining**
what was split. A join matches rows from two tables on a key.

How does it run? Three classic algorithms:

- **Nested loop** — for each row on one side, scan the other. Simple, great when
  one side is tiny.
- **Hash join** — build a hash table on the smaller table's key, then probe it
  with the larger. The workhorse for big equality joins.
- **Merge join** — sort both sides by the key, then walk them in lockstep. Great
  when inputs are already sorted.

The planner chooses; you just write `JOIN ... ON`. And beware the join type:
an **inner** join drops rows with no match, a **left** join keeps them — the
difference between "customers who ordered" and "all customers, orders or not."
Picking the wrong one is a top source of silently wrong reports.

*Go deeper: database normalization (1NF–3NF); "Database Internals" on join
algorithms.*
