"""SCAFFOLD (exercise stub) for sprint-3-airflow / scheduled-dag.
Reset with: ./scripts/check.sh start sprint-3-airflow scheduled-dag

The task already works. TODO: give this DAG a real schedule (a preset like @daily,
or a cron string) instead of None, so it runs on a cadence rather than only when
you trigger it by hand. See the lesson for the exact syntax.
"""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def build_report(**_):
    print("built the daily report")
    return "ok"


with DAG(
    dag_id="scheduled_report",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["exercise", "sprint-3"],
) as dag:
    PythonOperator(task_id="build_report", python_callable=build_report)
