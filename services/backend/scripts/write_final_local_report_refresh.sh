#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-local-report-refresh \
    --repo-root ../.. \
    --output .local/final-local-report-refresh.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final local report refresh exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-local-report-refresh.json"
  exit 0
fi

printf '%s\n' "final local report refresh failed before writing a usable report: exit $status" >&2
exit "$status"
