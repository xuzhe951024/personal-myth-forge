#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-resource-fill-guide \
    --repo-root ../.. \
    --output .local/final-resource-fill-guide.json \
    --markdown-output .local/final-resource-fill-guide.md
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted final resource fill guide exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-resource-fill-guide.json"
  printf '%s\n' "wrote services/backend/.local/final-resource-fill-guide.md"
  exit 0
fi

printf '%s\n' "final resource fill guide failed before writing a usable report: exit $status" >&2
exit "$status"
