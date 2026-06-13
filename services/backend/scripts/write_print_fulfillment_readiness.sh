#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli print-fulfillment-readiness \
    --repo-root ../.. \
    --output .local/print-fulfillment-readiness.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted print fulfillment readiness exit code $status"
  printf '%s\n' "wrote services/backend/.local/print-fulfillment-readiness.json"
  exit 0
fi

printf '%s\n' "print fulfillment readiness failed before writing a usable report: exit $status" >&2
exit "$status"
