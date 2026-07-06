# Data Engineering Glossary

Plain-English definitions for the terms you'll meet in the learning platform.

## Core ideas

- **Batch** — processing data in chunks on a schedule (e.g. "every night at 2am"),
  as opposed to continuously. Most warehouses are batch.
- **Streaming** — processing each event as it arrives, continuously, with low latency
  (e.g. Kafka/Redpanda). The opposite of batch.
- **ETL / ELT** — Extract, Transform, Load. In modern **ELT** you load raw data first,
  then transform it *inside* the warehouse (this is what dbt does).
- **Idempotent** — an operation you can run repeatedly and get the same result. The
  grader reseeds source data before each run precisely to keep checks idempotent.
- **Data contract** — an agreed shape and set of guarantees for a dataset (columns,
  types, "this key is never null / always unique"). Tests enforce it.

## Warehouse & modeling

- **Data warehouse** — a database optimized for analytics (reporting, aggregation)
  rather than serving an app. Postgres stands in for one here.
- **Data mart** — a focused slice of the warehouse for one team or subject area
  (e.g. `revenue_by_status`).
- **Schema** — a namespace inside a database that groups tables (e.g. `raw`,
  `analytics`). Not to be confused with a table's column definition.
- **Primary key** — a column whose value uniquely identifies each row (unique + not
  null). **Foreign key** — a column that references another table's primary key.
- **Source** (dbt) — a pointer to a raw table dbt reads from, e.g.
  `source('raw', 'orders')`.
- **Model** (dbt) — a `SELECT` statement dbt turns into a table or view.
- **Materialization** (dbt) — *how* a model is built: a `view` (a saved query) or a
  `table` (physically stored rows).
- **Staging model** — a first, lightly-cleaned layer over a raw source; marts build on
  staging.
- **Seed** — a small fixture dataset loaded into the warehouse (here, the raw orders
  and customers the exercises run against).

## Orchestration

- **Orchestration** — scheduling and running pipeline steps in the right order, with
  retries and monitoring. Airflow does this.
- **DAG** — Directed Acyclic Graph: a pipeline expressed as tasks with dependencies
  and no cycles. An Airflow pipeline *is* a DAG.
- **Task / Operator** (Airflow) — one unit of work in a DAG; the operator is the
  thing that runs (e.g. a `PythonOperator` runs a function).
- **Backfill** — running a pipeline for past dates it missed.

## Tools in this platform

- **Postgres** — the relational database standing in for the warehouse.
- **dbt** — transforms + tests SQL models in the warehouse.
- **Airflow** — orchestrates pipelines as DAGs.
- **Redpanda** — a Kafka-compatible streaming broker (used in later sprints).
- **Streamlit** — the Python framework behind this platform's web app.

## Grading terms (this platform)

- **Scaffold** — the incomplete starter file for a task; you edit it. It is *not* the
  answer.
- **Solution** — the reference answer, kept out of your workspace; the grader never
  reads it to decide pass/fail.
- **pass / fail / could-not-run** — pass = your work is correct; fail = it ran but is
  wrong; **could-not-run** = the stack was unavailable (never means your answer was
  wrong).
