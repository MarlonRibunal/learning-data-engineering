"""Reference solution for retry-dag."""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def do_work(**_):
    print("did the work")
    return "ok"


with DAG(
    dag_id="retry_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    PythonOperator(task_id="work", python_callable=do_work, retries=2)
