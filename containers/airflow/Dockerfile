FROM apache/airflow:2.7.0-python3.11
USER root
RUN apt-get update && apt-get install -y gcc g++ git
USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN mkdir -p /opt/airflow/dags /opt/airflow/scripts