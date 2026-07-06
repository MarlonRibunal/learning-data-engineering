### Filter rows with WHERE

`SELECT` chooses columns; `WHERE` chooses *rows*. It keeps only the rows where a
condition is true.

**Your task:** return the orders whose `status` is `'shipped'`.

```
SELECT *
FROM table_name
WHERE some_column = 'some_value';
```

Text values go in single quotes: `'shipped'`. This is the single most common thing
you'll do in SQL — slice a table down to the rows you care about.
