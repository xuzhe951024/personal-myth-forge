#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli ios-device-evidence-bundle \
    --repo-root ../.. \
    --output .local/ios-device-evidence-bundle.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted iOS device evidence bundle exit code $status"
  printf '%s\n' "wrote services/backend/.local/ios-device-evidence-bundle.json"
  exit 0
fi

printf '%s\n' "iOS device evidence bundle failed before writing a usable report: exit $status" >&2
exit "$status"
