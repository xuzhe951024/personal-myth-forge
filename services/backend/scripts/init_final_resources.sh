#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BACKEND_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$BACKEND_ROOT/../.." && pwd)
TEMPLATE="$BACKEND_ROOT/final-resources.env.example"
DESTINATION="$BACKEND_ROOT/.local/final-resources.env"
DESTINATION_LABEL="services/backend/.local/final-resources.env"
TEMPLATE_LABEL="services/backend/final-resources.env.example"

if [ ! -f "$TEMPLATE" ]; then
  printf '%s\n' "Missing $TEMPLATE_LABEL." >&2
  exit 2
fi

if git -C "$REPO_ROOT" ls-files --error-unmatch "$DESTINATION_LABEL" >/dev/null 2>&1; then
  printf '%s\n' "$DESTINATION_LABEL must stay untracked." >&2
  exit 1
fi

if [ -e "$DESTINATION" ]; then
  printf '%s\n' "$DESTINATION_LABEL already exists; refusing to overwrite." >&2
  printf '%s\n' "Review it or remove it before rerunning make final-resource-init." >&2
  exit 2
fi

mkdir -p "$(dirname -- "$DESTINATION")"
cp "$TEMPLATE" "$DESTINATION"
if command -v chmod >/dev/null 2>&1; then
  chmod 600 "$DESTINATION"
fi

printf '%s\n' "$DESTINATION_LABEL initialized from $TEMPLATE_LABEL."
printf '%s\n' "Fill the copy with final provider and iOS values; do not commit it."
printf '%s\n' "Next: make final-resources-preflight"
