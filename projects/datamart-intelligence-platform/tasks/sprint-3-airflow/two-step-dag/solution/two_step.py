"""Reference solution for two-step-dag (kept out of the dags path)."""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract(**_):
    return "raw data"


def load(**_):
    print("loaded raw data")
    return "ok"


with DAG(
    dag_id="two_step_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    load_task = PythonOperator(task_id="load", python_callable=load)
    extract_task >> load_task
