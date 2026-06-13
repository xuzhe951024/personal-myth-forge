#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-resource-apply-preview \
    --repo-root ../.. \
    --output .local/final-resource-apply-preview.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final resource apply preview exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-resource-apply-preview.json"
  exit 0
fi

printf '%s\n' "final resource apply preview failed before writing a usable report: exit $status" >&2
exit "$status"
