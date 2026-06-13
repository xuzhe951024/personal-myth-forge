#!/usr/bin/env sh
set -eu

mkdir -p services/backend/.local
set +e
(
  cd services/backend
  uv run python -m myth_forge_api.cli ios-device-launch-rehearsal-readiness \
    --repo-root ../.. \
    --output .local/ios-device-launch-rehearsal-readiness.json
)
status=$?
set -e

if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
  printf '%s\n' "accepted iOS device launch rehearsal readiness exit code $status"
  printf '%s\n' "wrote services/backend/.local/ios-device-launch-rehearsal-readiness.json"
  set +e
  (
    cd services/backend
    uv run python -m myth_forge_api.cli final-demo-launch \
      --mode local \
      --repo-root ../.. \
      --output .local/final-demo-launch-local.json
  )
  sync_status=$?
  set -e

  if [ "$sync_status" -eq 0 ] || [ "$sync_status" -eq 2 ]; then
    printf '%s\n' "accepted final demo launch sync exit code $sync_status"
    printf '%s\n' "wrote services/backend/.local/final-demo-launch-local.json"
    exit 0
  fi

  printf '%s\n' "final demo launch sync failed after iOS rehearsal readiness: exit $sync_status" >&2
  exit "$sync_status"
fi

printf '%s\n' "iOS device launch rehearsal readiness failed before writing a usable report: exit $status" >&2
exit "$status"
