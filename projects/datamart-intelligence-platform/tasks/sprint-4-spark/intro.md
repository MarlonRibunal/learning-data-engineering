**Big Data Processing with Spark.** So far you've transformed data one warehouse at a time. Spark is how data engineers process datasets too big for a single machine — it spreads the work across many cores (and, in production, many machines).

Here you'll write **PySpark** transforms that run on a local Spark engine (no cluster, no cloud — it runs right on your machine). You work with the **DataFrame API**: `select`, `filter`, `groupBy`, `join`, and control over `repartition`/`cache`. The same code you write here scales to terabytes on a real cluster — the API is identical.

Each task gives you one or more input DataFrames; you write a `transform(...)` function that returns the result. The grader runs it on a real Spark session and checks your rows.

> Needs **Java 17 or 21** (Spark 4 breaks on Java 22+) + `pip install pyspark`. On macOS: `brew install openjdk@17` and point `JAVA_HOME` at it. If Spark can't start, checks report *could not run* (not a wrong answer).
