FROM python:3.11-slim
WORKDIR /usr/app
RUN apt-get update && apt-get install -y git curl
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install dbt-core==1.5.0 dbt-bigquery==1.5.0
RUN mkdir -p /usr/app/dbt /usr/app/config
WORKDIR /usr/app/dbt