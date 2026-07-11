#!/usr/bin/env bash
# Boot the self-contained study container:
#   1. wire progress + submissions to the persistent /app/state volume,
#   2. start (and first-time initialize) the embedded Postgres warehouse,
#   3. launch the Streamlit learning app,
#   4. on shutdown, stop Postgres cleanly so the warehouse volume stays consistent.
set -e

STATE=/app/state
PGBIN="$(ls -d /usr/lib/postgresql/*/bin | head -1)"
export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
export PGDATA

pg_start() {
    su postgres -c "$PGBIN/pg_ctl -D '$PGDATA' -o \"-c listen_addresses='127.0.0.1'\" -w start >/dev/null"
}
pg_stop() {
    su postgres -c "$PGBIN/pg_ctl -D '$PGDATA' -m fast -w stop >/dev/null 2>&1" || true
}

mkdir -p "$STATE/submissions"

# --- persistence: keep progress + submitted code on the volume, symlinked in ---
[ -f "$STATE/.progress.json" ] || echo '{}' > "$STATE/.progress.json"
ln -sfn "$STATE/.progress.json" /app/.progress.json
[ -L /app/submissions ] || rm -rf /app/submissions
ln -sfn "$STATE/submissions" /app/submissions

# --- embedded warehouse ---
# A stale postmaster.pid from an unclean stop would block startup — clear it.
rm -f "$PGDATA/postmaster.pid" 2>/dev/null || true
if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "[study] first boot — initializing the embedded Postgres warehouse..."
    mkdir -p "$PGDATA"
    chown -R postgres:postgres "$STATE"
    su postgres -c "$PGBIN/initdb -D '$PGDATA' --auth=trust >/dev/null"
    pg_start
    su postgres -c "$PGBIN/psql -q -c \"CREATE ROLE airflow WITH LOGIN SUPERUSER PASSWORD 'airflow';\""
    su postgres -c "$PGBIN/createdb -O airflow datamart"
    PGPASSWORD=airflow "$PGBIN/psql" -q -h 127.0.0.1 -U airflow -d datamart \
        -f /app/projects/datamart-intelligence-platform/seeds/raw_seed.sql >/dev/null 2>&1 || true
    echo "[study] warehouse ready."
else
    chown -R postgres:postgres "$PGDATA" 2>/dev/null || true
    pg_start
    echo "[study] warehouse resumed (your progress is intact)."
fi

# --- clean shutdown on docker stop (SIGTERM) ---
shutdown() {
    echo "[study] stopping — flushing the warehouse so nothing is lost..."
    [ -n "$APP_PID" ] && kill "$APP_PID" 2>/dev/null || true
    pg_stop
    exit 0
}
trap shutdown TERM INT

echo "[study] open http://localhost:8501 to start learning."
streamlit run platform/runner/app.py \
    --server.port 8501 --server.address 0.0.0.0 --server.headless true &
APP_PID=$!
wait "$APP_PID" || true
# reached if Streamlit exits on its own — still leave the warehouse consistent
pg_stop
