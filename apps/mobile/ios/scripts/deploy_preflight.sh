#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
IOS_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
CONFIG_DIR="$IOS_ROOT/Config"
BASE_CONFIG="$CONFIG_DIR/Deployment.xcconfig"
LOCAL_CONFIG="$CONFIG_DIR/Deployment.local.xcconfig"

get_value() {
  key="$1"
  value=""
  for file in "$BASE_CONFIG" "$LOCAL_CONFIG"; do
    if [ -f "$file" ]; then
      found=$(awk -F '=' -v key="$key" '
        $0 !~ /^[[:space:]]*(\/\/|#)/ {
          lhs=$1
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", lhs)
          if (lhs == key) {
            rhs=$2
            sub(/^[[:space:]]+/, "", rhs)
            sub(/[[:space:]]+$/, "", rhs)
            print rhs
          }
        }
      ' "$file" | tail -n 1)
      if [ -n "$found" ]; then
        value="$found"
      fi
    fi
  done
  printf '%s' "$value"
}

if [ ! -f "$BASE_CONFIG" ]; then
  printf '%s\n' "Missing Deployment.xcconfig." >&2
  exit 1
fi

REPOSITORY_ROOT=$(git -C "$IOS_ROOT" rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$REPOSITORY_ROOT" ] &&
  git -C "$REPOSITORY_ROOT" ls-files --error-unmatch "apps/mobile/ios/Config/Deployment.local.xcconfig" >/dev/null 2>&1; then
  printf '%s\n' "Deployment.local.xcconfig must stay untracked." >&2
  exit 1
fi

team=$(get_value DEVELOPMENT_TEAM)
bundle_id=$(get_value PRODUCT_BUNDLE_IDENTIFIER)
backend_url=$(get_value PMF_BACKEND_BASE_URL)

missing=0
if [ -z "$team" ]; then
  printf '%s\n' "Missing DEVELOPMENT_TEAM in Deployment.local.xcconfig." >&2
  missing=1
fi
if [ -z "$bundle_id" ]; then
  printf '%s\n' "Missing PRODUCT_BUNDLE_IDENTIFIER." >&2
  missing=1
fi
if [ -z "$backend_url" ]; then
  printf '%s\n' "Missing PMF_BACKEND_BASE_URL." >&2
  missing=1
fi
case "$backend_url" in
  http://127.0.0.1:*|http://localhost:*|https://127.0.0.1:*|https://localhost:*)
    printf '%s\n' "PMF_BACKEND_BASE_URL must be reachable from iPhone, not loopback." >&2
    missing=1
    ;;
esac

if [ "$missing" -ne 0 ]; then
  exit 2
fi

printf '%s\n' "iOS deploy preflight passed."
printf '%s\n' "Bundle: $bundle_id"
printf '%s\n' "Backend: $backend_url"
