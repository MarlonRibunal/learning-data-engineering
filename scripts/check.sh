#!/usr/bin/env bash
# Learn-by-doing grader — host-side entrypoint.
#
#   ./scripts/check.sh start <sprint> <task>   copy the scaffold into your workspace
#   ./scripts/check.sh check <sprint> <task>   grade your submission
#
# The grader runs on the host and drives the stack containers via
# `docker compose exec` (no socket mount). It needs `pyyaml` (and `psycopg2` for
# SQL checks) — see platform/requirements.txt.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$REPO_ROOT/platform${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m grader.cli --repo-root "$REPO_ROOT" "$@"
