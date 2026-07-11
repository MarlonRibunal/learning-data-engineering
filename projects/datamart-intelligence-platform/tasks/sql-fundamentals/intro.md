**SQL is the language of data.** Before you orchestrate or transform anything, you
need to ask precise questions of a database. These tasks build the core moves —
filtering, aggregating, grouping — that every later sprint depends on.

Tip: hit **▶ Run query** in a task to run your SQL against the real warehouse and see
the actual rows it returns — experiment freely, then **Check my work** when it looks
right. (Needs the stack up: `./platform.sh up`.)

**Explore the warehouse:** open **PGAdmin** at [localhost:8081](http://localhost:8081)
(`admin@datamart.com` / `admin`) — also linked from the **Platform** page — to browse
the schema visually, inspect tables, and run ad-hoc queries against the same warehouse
the grader uses.
