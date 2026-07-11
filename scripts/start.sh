#!/usr/bin/env bash
# Bring the platform services up (detached). For the graded learning app,
# use ./platform.sh (it host-runs the lesson-runner on 8501).
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."
echo "🔧 Starting platform services..."
docker compose up -d
echo "✅ Services started:"
echo "   Airflow          http://localhost:8080  (admin / admin)"
echo "   PGAdmin          http://localhost:8081  (admin@datamart.com / admin)"
echo "   Redpanda Console http://localhost:8082"
echo
echo "▶ Learning app:  ./platform.sh   →  http://localhost:8501"
