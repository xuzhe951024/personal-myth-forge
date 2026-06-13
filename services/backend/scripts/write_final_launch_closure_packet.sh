#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-launch-closure-packet \
    --repo-root ../.. \
    --output .local/final-launch-closure-packet.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final launch closure packet exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-launch-closure-packet.json"
  exit 0
fi

printf '%s\n' "final launch closure packet failed before writing a usable report: exit $status" >&2
exit "$status"
