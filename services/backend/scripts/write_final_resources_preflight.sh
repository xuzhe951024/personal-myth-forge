#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-resources-preflight \
    --repo-root ../.. \
    --output .local/final-resources-preflight.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final resources preflight exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-resources-preflight.json"
  exit 0
fi

printf '%s\n' "final resources preflight failed before writing a usable report: exit $status" >&2
exit "$status"
