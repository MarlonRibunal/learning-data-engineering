#!/usr/bin/env bash
# Boot the self-contained study container:
#   1. wire progress + submissions to the persistent /app/state volume,
#   2. start (and first-time initialize) the embedded Postgres warehouse,
#   3. launch the Streamlit learning app.
set -e

STATE=/app/state
PGBIN="$(ls -d /usr/lib/postgresql/*/bin | head -1)"
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"

mkdir -p "$STATE/submissions"

# --- persistence: keep progress + submitted code on the volume, symlinked in ---
[ -f "$STATE/.progress.json" ] || echo '{}' > "$STATE/.progress.json"
ln -sfn "$STATE/.progress.json" /app/.progress.json
[ -L /app/submissions ] || rm -rf /app/submissions
ln -sfn "$STATE/submissions" /app/submissions

# --- embedded warehouse ---
export PGDATA
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "[study] first boot — initializing the embedded Postgres warehouse..."
    mkdir -p "$PGDATA"
    chown -R postgres:postgres "$STATE"
    su postgres -c "$PGBIN/initdb -D '$PGDATA' --auth=trust >/dev/null"
    su postgres -c "$PGBIN/pg_ctl -D '$PGDATA' -o \"-c listen_addresses='127.0.0.1'\" -w start >/dev/null"
    su postgres -c "$PGBIN/psql -q -c \"CREATE ROLE airflow WITH LOGIN SUPERUSER PASSWORD 'airflow';\""
    su postgres -c "$PGBIN/createdb -O airflow datamart"
    PGPASSWORD=airflow "$PGBIN/psql" -q -h 127.0.0.1 -U airflow -d datamart \
        -f /app/projects/datamart-intelligence-platform/seeds/raw_seed.sql >/dev/null 2>&1 || true
    echo "[study] warehouse ready."
else
    chown -R postgres:postgres "$PGDATA" 2>/dev/null || true
    su postgres -c "$PGBIN/pg_ctl -D '$PGDATA' -o \"-c listen_addresses='127.0.0.1'\" -w start >/dev/null"
    echo "[study] warehouse resumed (your progress is intact)."
fi

echo "[study] open http://localhost:8501 to start learning."
exec streamlit run platform/runner/app.py \
    --server.port 8501 --server.address 0.0.0.0 --server.headless true
