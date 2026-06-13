#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-showcase-readiness \
    --repo-root ../.. \
    --output .local/final-showcase-readiness.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final showcase readiness exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-showcase-readiness.json"
  exit 0
fi

printf '%s\n' "final showcase readiness failed before writing a usable report: exit $status" >&2
exit "$status"
