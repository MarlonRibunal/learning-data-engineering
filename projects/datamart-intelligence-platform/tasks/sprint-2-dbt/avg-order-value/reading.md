## sources, ref, and the dbt DAG

The two functions you'll use most in dbt are `source()` and `ref()`, and they do
more than name tables — they build a **dependency graph**.

- **`{{ source('raw', 'orders') }}`** declares "this reads a raw external table."
  You register sources once, so dbt knows where the pipeline *starts*.
- **`{{ ref('stg_orders') }}`** declares "this reads another dbt model." dbt
  substitutes the real (possibly environment-specific) table name *and* records
  the edge: this model depends on `stg_orders`.

From all those `ref`s, dbt assembles a **DAG** (directed acyclic graph) of your
models. That graph is quietly powerful:

- **Order of execution** — `dbt run` topologically sorts the DAG so a model never
  builds before its inputs. (You implement that sort yourself in the Advanced
  sprint.)
- **Lineage** — you can trace any column back to its raw source, and forward to
  every dashboard it feeds.
- **Selective builds** — `dbt run --select model+` rebuilds a model and only
  what's downstream of it.

So writing `ref()`/`source()` instead of hard-coding table names is what turns a
pile of SQL files into a coherent, ordered, traceable pipeline.

*Go deeper: dbt "ref", "sources", and the model DAG.*
