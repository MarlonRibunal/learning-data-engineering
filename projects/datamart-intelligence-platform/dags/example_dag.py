from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator

def print_hello():
    print("Hello from Data Engineering learning environment!")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG('example_dag', default_args=default_args, schedule_interval=timedelta(days=1)) as dag:
    start = DummyOperator(task_id='start')
    hello_task = PythonOperator(task_id='print_hello', python_callable=print_hello)
    end = DummyOperator(task_id='end')
    start >> hello_task >> end