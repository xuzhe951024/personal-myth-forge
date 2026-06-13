#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli resource-handoff \
    --repo-root ../.. \
    --output .local/resource-handoff.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted resource handoff exit code $status"
  printf '%s\n' "wrote services/backend/.local/resource-handoff.json"
  exit 0
fi

printf '%s\n' "resource handoff failed before writing a usable report: exit $status" >&2
exit "$status"
