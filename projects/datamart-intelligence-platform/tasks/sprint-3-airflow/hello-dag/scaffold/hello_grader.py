"""SCAFFOLD (exercise stub) for sprint-3-airflow / hello-dag.

A fresh clone triggers this DAG and it FAILS on purpose, so the grader does not
pass until you make the task succeed.

Reset to this stub any time with:
    ./scripts/check.sh start sprint-3-airflow hello-dag

TODO: make `run` succeed — return a value instead of raising.
"""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def run(**context):
    # TODO: replace this with real work that returns normally.
    raise NotImplementedError("finish the hello-dag task so it succeeds")


with DAG(
    dag_id="hello_grader",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    PythonOperator(task_id="say_hello", python_callable=run)
