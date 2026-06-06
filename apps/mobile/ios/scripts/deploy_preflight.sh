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

health_url() {
  case "$1" in
    */) printf '%shealth' "$1" ;;
    *) printf '%s/health' "$1" ;;
  esac
}

check_backend_health() {
  url=$(health_url "$backend_url")
  body=""
  if command -v python3 >/dev/null 2>&1; then
    body=$(python3 - "$url" <<'PY' 2>/dev/null || true
import sys
import urllib.request

url = sys.argv[1]
with urllib.request.urlopen(url, timeout=3) as response:
    print(response.read(512).decode("utf-8", errors="replace"))
PY
)
  elif command -v curl >/dev/null 2>&1; then
    body=$(curl --fail --silent --show-error --max-time 3 "$url" 2>/dev/null | head -c 512 || true)
  else
    printf '%s\n' "Backend health check failed. python3 or curl is required." >&2
    return 1
  fi

  compact=$(printf '%s' "$body" | tr -d '[:space:]')
  case "$compact" in
    *'"status":"ok"'*) return 0 ;;
  esac
  printf '%s\n' "Backend health check failed. Start backend-device-demo and verify PMF_BACKEND_BASE_URL." >&2
  return 1
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
final_launch_mode=$(get_value PMF_FINAL_LAUNCH_MODE)
final_launch_mode=$(printf '%s' "$final_launch_mode" | tr '[:upper:]' '[:lower:]')

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
case "$final_launch_mode" in
  local|configured) ;;
  *)
    printf '%s\n' "PMF_FINAL_LAUNCH_MODE must be local or configured." >&2
    missing=1
    ;;
esac

if [ "$missing" -ne 0 ]; then
  exit 2
fi

if ! check_backend_health; then
  exit 2
fi

printf '%s\n' "iOS deploy preflight passed."
printf '%s\n' "Bundle: $bundle_id"
printf '%s\n' "Backend: $backend_url"
printf '%s\n' "Final launch mode: $final_launch_mode"
printf '%s\n' "Backend health: ok"
