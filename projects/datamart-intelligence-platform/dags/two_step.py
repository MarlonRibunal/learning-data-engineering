"""SCAFFOLD (exercise stub) for sprint-3-airflow / two-step-dag.
Reset with: ./scripts/check.sh start sprint-3-airflow two-step-dag

TODO: (1) make `load` finish instead of raising, and
      (2) wire the dependency so extract runs before load:  extract >> load
"""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract(**_):
    return "raw data"


def load(**_):
    raise NotImplementedError("finish load, then set the dependency: extract >> load")


with DAG(
    dag_id="two_step_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    extract_task = PythonOperator(task_id="extract", python_callable=extract)
    load_task = PythonOperator(task_id="load", python_callable=load)
    # TODO: wire the dependency here
