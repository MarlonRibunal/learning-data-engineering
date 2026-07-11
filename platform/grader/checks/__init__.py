"""Importing this package registers all built-in check types.

New check kinds are added by creating a module here and importing it below.
"""

from . import (  # noqa: F401  (import for side effects: registers check types)
    airflow_check,
    data_test,
    dbt_check,
    file_check,
    job_api,
    pyfunc,
    redpanda_check,
    spark_check,
    spark_streaming,
    sql_check,
    sql_ingest,
    sql_result,
)
