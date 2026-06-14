#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-demo-launch \
    --mode configured \
    --repo-root ../.. \
    --output .local/final-demo-launch-configured.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted configured final demo launch exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-demo-launch-configured.json"
  exit 0
fi

printf '%s\n' "configured final demo launch failed before writing a usable report: exit $status" >&2
exit "$status"
