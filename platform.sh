#!/usr/bin/env bash
#
# One command to start learning.
#
#   ./platform.sh            set up + bring the stack up + open the web app
#   ./platform.sh setup      just create the venv and install deps
#   ./platform.sh up         just bring the Docker stack up (and wait for it)
#   ./platform.sh runner     just open the web app (assumes setup already ran)
#   ./platform.sh list       list tasks and your progress
#   ./platform.sh status     progress dashboard + your next task
#   ./platform.sh down       stop the Docker stack   (add -v to wipe data)
#
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
VENV="$ROOT/.venv"
PY="${PYTHON:-python3}"

# The full platform stack: the warehouse + dbt + the Airflow UI & scheduler +
# the Redpanda broker & console + PGAdmin. The lesson-runner web app is host-run
# (below) on 8501, so we don't start the compose `streamlit` service here.
# Students reach every UI from the app's "Platform" page.
STACK_SERVICES="postgres dbt-service airflow-init airflow-webserver airflow-scheduler \
redpanda redpanda-console pgadmin dashboard"

say() { printf '\033[36m▸ %s\033[0m\n' "$*"; }
die() { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

setup() {
  if [ ! -d "$VENV" ]; then
    say "creating virtualenv (.venv)"
    "$PY" -m venv "$VENV"
  fi
  say "installing platform dependencies"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r platform/requirements.txt
  printf '\033[32m✓ environment ready\033[0m\n'
}

stack_up() {
  docker info >/dev/null 2>&1 || die "Docker isn't running — start Docker Desktop or OrbStack, then re-run."
  say "starting the data stack (first run builds images; grab a coffee)"
  docker compose up -d --build $STACK_SERVICES
  say "waiting for Postgres to be ready"
  for _ in $(seq 1 60); do
    if docker compose exec -T postgres pg_isready -U airflow >/dev/null 2>&1; then
      printf '\033[32m✓ stack is up\033[0m\n'
      printf '  the platform surfaces (also linked in the app):\n'
      printf '    Airflow          http://localhost:8080  (admin / admin)\n'
      printf '    PGAdmin          http://localhost:8081  (admin@datamart.com / admin)\n'
      printf '    Redpanda Console http://localhost:8082\n'
      return 0
    fi
    sleep 2
  done
  die "Postgres did not become ready in time — check: docker compose logs postgres"
}

runner() {
  [ -x "$VENV/bin/streamlit" ] || die "run ./platform.sh setup first"
  say "opening the web app at http://localhost:8501  (Ctrl-C to stop)"
  exec "$VENV/bin/streamlit" run platform/runner/app.py
}

case "${1:-start}" in
  setup)  setup ;;
  up)     stack_up ;;
  runner) setup; runner ;;
  list|status)
    setup
    PYTHONPATH="$ROOT/platform" "$VENV/bin/python" -m grader.cli --repo-root "$ROOT" "$1" ;;
  down)   shift; docker compose down "$@" ;;
  start|"")
    setup
    stack_up
    runner
    ;;
  *) die "usage: ./platform.sh [start|setup|up|runner|list|status|down]" ;;
esac
