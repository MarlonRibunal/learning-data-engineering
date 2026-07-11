# Select specific columns

**The scenario.** Every data question starts the same way: *"show me these
columns from this table."* Before you can filter, group, or join, you have to be
able to ask for exactly the fields you want — the foundation everything else
builds on.

## The two clauses

Every query needs at least two parts:

```sql
SELECT column_a, column_b   -- which columns you want
FROM   table_name;          -- which table they come from
```

- **`SELECT`** lists the columns, in the order you want them back.
- **`FROM`** names the table to read.

## Why not `SELECT *`?

`SELECT *` returns *every* column. It's fine for poking around, but real
pipelines name their columns explicitly, for good reasons:

- **Clarity** — the next engineer sees exactly what the query depends on.
- **Stability** — if someone adds a column upstream, your query's shape doesn't
  silently change.
- **Cost** — you don't drag columns across the network that nobody uses.

Naming columns is a habit worth building from your very first query.

## The data

The `orders` table has: `order_id`, `customer_id`, `order_date`,
`total_amount`, `status`, `category`.

## Your task

Return **`order_id`, `status`, and `total_amount`** for every order — those three
columns, named explicitly.

```sql
SELECT order_id, status, total_amount
FROM orders;
```
