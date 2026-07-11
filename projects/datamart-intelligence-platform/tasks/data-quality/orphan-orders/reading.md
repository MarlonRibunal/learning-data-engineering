## Referential integrity

An **orphan** is a child row whose parent doesn't exist — an order pointing at a
`customer_id` that isn't in `customers`. **Referential integrity** is the property
that every foreign key resolves to a real row, and losing it breaks the joins your
entire analytics layer depends on.

In a transactional database, a **`FOREIGN KEY` constraint** enforces this — the
database physically refuses an order with a non-existent customer. But data
warehouses often **drop foreign keys on purpose**: they slow big loads, and data
arrives out of order (an order streams in before its customer row does). So the
guarantee the OLTP database gave you for free becomes *your* job to test.

The consequence of an orphan is subtle and dangerous: an **inner join** silently
*drops* the orphaned order (no matching customer, no output row), so your "total
revenue" quietly under-counts — no error, just a wrong number. A referential test
(orders with no matching customer) surfaces exactly those rows before they distort
a report.

This is the **consistency** dimension across tables, and it's why star-schema
fact/dimension modeling takes referential integrity so seriously.

*Go deeper: foreign keys; why warehouses skip them; inner-join drop as a bug.*
