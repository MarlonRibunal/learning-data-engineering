"""Reference solution for sprint-3-airflow / hello-dag (kept out of the dags path)."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def run(**context):
    print("hello from the grader DAG")
    return "ok"


with DAG(
    dag_id="hello_grader",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    PythonOperator(task_id="say_hello", python_callable=run)
