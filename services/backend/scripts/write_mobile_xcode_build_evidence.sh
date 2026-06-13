#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli mobile-xcode-build-evidence \
    --repo-root ../.. \
    --output .local/mobile-xcode-build-evidence.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted mobile Xcode build evidence exit code $status"
  printf '%s\n' "wrote services/backend/.local/mobile-xcode-build-evidence.json"
  exit 0
fi

printf '%s\n' "mobile Xcode build evidence failed before writing a usable report: exit $status" >&2
exit "$status"
