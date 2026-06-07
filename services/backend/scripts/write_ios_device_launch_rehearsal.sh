#!/usr/bin/env sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../../.." && pwd)

cd "$repo_root"
mkdir -p services/backend/.local

run_report_command() {
  label="$1"
  shift

  set +e
  "$@"
  status=$?
  set -e

  if [ "$status" -eq 0 ] || [ "$status" -eq 2 ]; then
    printf '%s\n' "accepted $label exit code $status"
    return 0
  fi

  printf '%s\n' "$label failed before writing usable reports: exit $status" >&2
  exit "$status"
}

run_report_command "final rehearsal" make final-rehearsal-local

run_report_command "configured preflight" sh -c '
  cd services/backend &&
  uv run python -m myth_forge_api.cli final-configured-preflight \
    --repo-root ../.. \
    --output .local/final-configured-preflight.json
'

run_report_command "final handoff index" sh -c '
  cd services/backend &&
  uv run python -m myth_forge_api.cli final-handoff-index \
    --repo-root ../.. \
    --output .local/final-handoff-index.json
'

run_report_command "iOS device launch certificate" sh -c '
  cd services/backend &&
  uv run python -m myth_forge_api.cli ios-device-launch-certificate \
    --repo-root ../.. \
    --output .local/ios-device-launch-certificate.json
'

run_report_command "iOS device launch rehearsal" sh -c '
  cd services/backend &&
  uv run python -m myth_forge_api.cli ios-device-launch-rehearsal \
    --repo-root ../.. \
    --output .local/ios-device-launch-rehearsal.json
'

run_report_command "final launch rehearsal sync" sh -c '
  cd services/backend &&
  uv run python -m myth_forge_api.cli final-demo-launch \
    --mode local \
    --repo-root ../.. \
    --output .local/final-demo-launch-local.json
'

printf '%s\n' "wrote services/backend/.local/ios-device-launch-rehearsal.json"
printf '%s\n' "wrote services/backend/.local/final-demo-launch-local.json"
