#!/usr/bin/env sh
set -eu

if [ -z "${PRINT_SOURCE_ASSET_URI:-}" ]; then
  printf '%s\n' "PRINT_SOURCE_ASSET_URI is required." >&2
  exit 2
fi

if [ -z "${PRINT_CANDIDATE_URI:-}" ]; then
  printf '%s\n' "PRINT_CANDIDATE_URI is required." >&2
  exit 2
fi

mkdir -p services/backend/.local
cd services/backend
uv run python -m myth_forge_api.cli print-quote-request-configured \
  --source-asset-uri "$PRINT_SOURCE_ASSET_URI" \
  --print-candidate-uri "$PRINT_CANDIDATE_URI" \
  --repo-root ../.. \
  --format "${PRINT_CANDIDATE_FORMAT:-3mf}" \
  --quantity "${PRINT_QUANTITY:-1}" \
  --material "${PRINT_MATERIAL:-standard_resin}" \
  --finish "${PRINT_FINISH:-matte}" \
  --ship-to-country "${PRINT_SHIP_TO_COUNTRY:-US}" \
  --output .local/print-quote-request-configured.json
printf '%s\n' "wrote services/backend/.local/print-quote-request-configured.json"
