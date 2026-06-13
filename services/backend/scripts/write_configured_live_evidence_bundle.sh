#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli configured-live-evidence-bundle \
    --repo-root ../.. \
    --output .local/configured-live-evidence-bundle.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted configured live evidence bundle exit code $status"
  printf '%s\n' "wrote services/backend/.local/configured-live-evidence-bundle.json"
  exit 0
fi

printf '%s\n' "configured live evidence bundle failed before writing a usable report: exit $status" >&2
exit "$status"
