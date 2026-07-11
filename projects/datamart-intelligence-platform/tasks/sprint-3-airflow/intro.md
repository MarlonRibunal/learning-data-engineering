**Pipelines have to run on a schedule, in order, and recover when they fail.**
Airflow orchestrates them as DAGs (directed graphs of tasks). You'll make a real DAG
run green — the same thing you'd watch for in production.

**See it run:** open the **Airflow UI** at [localhost:8080](http://localhost:8080)
(`admin` / `admin`) — also linked from the app's **Platform** page — to unpause your
DAG, trigger a run, and watch each task turn green in the Graph view. That live view
is exactly what you'd monitor on the job.
