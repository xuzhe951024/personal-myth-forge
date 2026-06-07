#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli ios-deploy-runbook \
    --mode local \
    --repo-root ../.. \
    --output .local/ios-deploy-runbook-local.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted iOS deploy runbook exit code $status"
  printf '%s\n' "wrote services/backend/.local/ios-deploy-runbook-local.json"
  exit 0
fi

printf '%s\n' "iOS deploy runbook failed before writing a usable report: exit $status" >&2
exit "$status"
