## The logical order of a query

`HAVING` confuses people until you learn the **logical order** SQL evaluates a
query in — which is *not* the order you write it:

```
FROM      → pick the tables
WHERE     → filter rows
GROUP BY  → form groups
HAVING    → filter groups
SELECT    → compute output columns
ORDER BY  → sort
LIMIT     → cut
```

Written order (`SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ...`) is almost
the reverse of evaluation order. Once you internalize this pipeline, a dozen
mysteries resolve at once:

- **Why `HAVING` and not `WHERE` for `COUNT(*) > 1`?** `WHERE` runs *before*
  `GROUP BY`, when groups — and their counts — don't exist yet. `HAVING` runs
  *after*, so it can test aggregates. Two filter clauses, two different stages.
- **Why can't you use a `SELECT` alias in `WHERE`?** `SELECT` is computed *after*
  `WHERE`, so the alias isn't defined yet. (Many engines *do* let you use it in
  `ORDER BY`, which runs after `SELECT`.)
- **Why does `GROUP BY` restrict what `SELECT` can show?** Because by the time
  `SELECT` runs, rows are already collapsed into groups.

This mental model — a fixed pipeline of stages — is the single most useful thing
to carry into every SQL query you write.

*Go deeper: search "SQL logical query processing order" — it's worth memorizing.*
