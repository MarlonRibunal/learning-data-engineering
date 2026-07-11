#!/usr/bin/env bash
#
# One command to start the platform. Delegates to ./platform.sh, which sets up
# the Python env, brings the full Docker stack up (Airflow, PGAdmin, Redpanda +
# Console, Postgres, dbt), and opens the learning app at http://localhost:8501.
#
# Kept for muscle memory / older docs — ./platform.sh is the canonical entry.
#
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
exec ./platform.sh "$@"
