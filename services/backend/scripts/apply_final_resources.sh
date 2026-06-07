#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BACKEND_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$BACKEND_ROOT/../.." && pwd)
DEFAULT_RESOURCES_FILE="$BACKEND_ROOT/.local/final-resources.env"
BACKEND_WRITER="$BACKEND_ROOT/scripts/write_backend_env.sh"
IOS_WRITER="$REPO_ROOT/apps/mobile/ios/scripts/write_deploy_local_config.sh"

usage() {
  cat <<'EOF'
Usage: apply_final_resources.sh [--resources-file PATH]

Default resources file:
  services/backend/.local/final-resources.env

Run `make final-resource-init` to create the default file, fill values,
then run this script or `make final-apply-resources`.
EOF
}

resources_file="$DEFAULT_RESOURCES_FILE"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --resources-file)
      if [ "$#" -lt 2 ]; then
        printf '%s\n' "Missing value for --resources-file." >&2
        exit 2
      fi
      resources_file="$2"
      shift 2
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      printf '%s\n' "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if [ ! -f "$resources_file" ]; then
  printf '%s\n' "Missing final resources file: $resources_file" >&2
  printf '%s\n' "Run make final-resource-init to create services/backend/.local/final-resources.env." >&2
  exit 2
fi

meshy_key=""
openai_key=""
openai_base_url=""
print_provider="local"
treatstock_key=""
treatstock_base_url="https://www.treatstock.com"
sculpteo_key=""
team=""
bundle_id=""
backend_url=""
final_launch_mode="local"
capture_storage_dir=""
myth_session_storage_dir=""

while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    ""|\#*) continue ;;
    export\ *) line=${line#export } ;;
  esac
  case "$line" in
    *=*) ;;
    *)
      printf '%s\n' "Invalid final resource line. Expected KEY=value." >&2
      exit 2
      ;;
  esac
  key=${line%%=*}
  value=${line#*=}
  case "$key" in
    MESHY_API_KEY) meshy_key="$value" ;;
    OPENAI_API_KEY) openai_key="$value" ;;
    OPENAI_API_BASE_URL) openai_base_url="$value" ;;
    PRINT_PROVIDER) print_provider="$value" ;;
    TREATSTOCK_API_KEY) treatstock_key="$value" ;;
    TREATSTOCK_API_BASE_URL) treatstock_base_url="$value" ;;
    SCULPTEO_API_KEY) sculpteo_key="$value" ;;
    DEVELOPMENT_TEAM) team="$value" ;;
    PRODUCT_BUNDLE_IDENTIFIER) bundle_id="$value" ;;
    PMF_BACKEND_BASE_URL) backend_url="$value" ;;
    PMF_FINAL_LAUNCH_MODE) final_launch_mode="$value" ;;
    CAPTURE_STORAGE_DIR) capture_storage_dir="$value" ;;
    MYTH_SESSION_STORAGE_DIR) myth_session_storage_dir="$value" ;;
    *)
      printf '%s\n' "Unknown final resource key: $key" >&2
      exit 2
      ;;
  esac
done <"$resources_file"

missing=0
if [ -z "$meshy_key" ]; then
  printf '%s\n' "Missing MESHY_API_KEY in final resources." >&2
  missing=1
fi
if [ -z "$openai_key" ]; then
  printf '%s\n' "Missing OPENAI_API_KEY in final resources." >&2
  missing=1
fi
if [ -z "$team" ]; then
  printf '%s\n' "Missing DEVELOPMENT_TEAM in final resources." >&2
  missing=1
fi
if [ -z "$bundle_id" ]; then
  printf '%s\n' "Missing PRODUCT_BUNDLE_IDENTIFIER in final resources." >&2
  missing=1
fi
case "$bundle_id" in
  com.example|com.example.*)
    printf '%s\n' "PRODUCT_BUNDLE_IDENTIFIER must be a unique app bundle id, not com.example.*." >&2
    missing=1
    ;;
esac
if [ -z "$backend_url" ]; then
  printf '%s\n' "Missing PMF_BACKEND_BASE_URL in final resources." >&2
  missing=1
fi

print_provider=$(printf '%s' "$print_provider" | tr '[:upper:]' '[:lower:]')
case "$print_provider" in
  local|treatstock) ;;
  *)
    printf '%s\n' "Unsupported PRINT_PROVIDER in final resources: $print_provider" >&2
    missing=1
    ;;
esac

final_launch_mode=$(printf '%s' "$final_launch_mode" | tr '[:upper:]' '[:lower:]')
case "$final_launch_mode" in
  local|configured) ;;
  *)
    printf '%s\n' "Unsupported PMF_FINAL_LAUNCH_MODE in final resources: $final_launch_mode" >&2
    missing=1
    ;;
esac

if [ "$print_provider" = "treatstock" ] && [ -z "$treatstock_key" ]; then
  printf '%s\n' "TREATSTOCK_API_KEY is required when PRINT_PROVIDER=treatstock." >&2
  missing=1
fi

case "$backend_url" in
  http://192.168.1.10:8080|http://192.168.1.10:8080/)
    printf '%s\n' "PMF_BACKEND_BASE_URL must be changed from the example LAN URL." >&2
    missing=1
    ;;
  http://127.0.0.1*|http://localhost*|https://127.0.0.1*|https://localhost*)
    printf '%s\n' "PMF_BACKEND_BASE_URL must be reachable from iPhone, not loopback." >&2
    missing=1
    ;;
esac

if [ "$missing" -ne 0 ]; then
  exit 2
fi

MESHY_API_KEY="$meshy_key" \
OPENAI_API_KEY="$openai_key" \
OPENAI_API_BASE_URL="$openai_base_url" \
PRINT_PROVIDER="$print_provider" \
TREATSTOCK_API_KEY="$treatstock_key" \
TREATSTOCK_API_BASE_URL="$treatstock_base_url" \
SCULPTEO_API_KEY="$sculpteo_key" \
CAPTURE_STORAGE_DIR="$capture_storage_dir" \
MYTH_SESSION_STORAGE_DIR="$myth_session_storage_dir" \
  sh "$BACKEND_WRITER"

DEVELOPMENT_TEAM="$team" \
PRODUCT_BUNDLE_IDENTIFIER="$bundle_id" \
PMF_BACKEND_BASE_URL="$backend_url" \
PMF_FINAL_LAUNCH_MODE="$final_launch_mode" \
  sh "$IOS_WRITER"

printf '%s\n' "Final resources applied."
printf '%s\n' "Resources file: configured (redacted)"
