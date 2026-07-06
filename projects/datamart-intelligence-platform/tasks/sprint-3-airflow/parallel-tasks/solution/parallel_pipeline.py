"""SCAFFOLD (exercise stub) for sprint-3-airflow / parallel-tasks.
Reset with: ./scripts/check.sh start sprint-3-airflow parallel-tasks

TODO: run `left` and `right` in parallel AFTER `start`. Fan them out with a list
dependency (see the lesson for the syntax).
"""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def start(**_):
    return "go"


def left(**_):
    print("left branch")
    return "l"


def right(**_):
    print("right branch")
    return "r"


with DAG(
    dag_id="parallel_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    start_task = PythonOperator(task_id="start", python_callable=start)
    left_task = PythonOperator(task_id="left", python_callable=left)
    right_task = PythonOperator(task_id="right", python_callable=right)
    start_task >> [left_task, right_task]
