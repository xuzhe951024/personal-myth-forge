#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli final-acceptance \
    --profile quick \
    --provider-mode configured \
    --require-real-core \
    --allow-live-provider-calls \
    --repo-root ../.. \
    --output .local/final-acceptance-configured.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted configured final acceptance exit code $status"
  printf '%s\n' "wrote services/backend/.local/final-acceptance-configured.json"
  exit 0
fi

printf '%s\n' "configured final acceptance failed before writing a usable report: exit $status" >&2
exit "$status"
