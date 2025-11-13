# Airflow Cheatsheet

## Basic DAG Structure
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG('my_dag', default_args=default_args, schedule_interval='@daily') as dag:
    task1 = PythonOperator(task_id='task1', python_callable=my_function)