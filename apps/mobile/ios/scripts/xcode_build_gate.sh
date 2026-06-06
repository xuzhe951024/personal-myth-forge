#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
IOS_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
DEFAULT_DEVELOPER_DIR="/Applications/Xcode.app/Contents/Developer"
XCODE_DEVELOPER_DIR="${DEVELOPER_DIR:-$DEFAULT_DEVELOPER_DIR}"
XCODEBUILD="$XCODE_DEVELOPER_DIR/usr/bin/xcodebuild"
DERIVED_DATA_PATH="$IOS_ROOT/.build/xcode-derived-data"

if [ ! -x "$XCODEBUILD" ]; then
  printf '%s\n' "Xcode build gate could not find xcodebuild at $XCODEBUILD." >&2
  printf '%s\n' "Install Xcode or run with DEVELOPER_DIR=/path/to/Xcode.app/Contents/Developer." >&2
  exit 127
fi

mkdir -p "$DERIVED_DATA_PATH"

exec "$XCODEBUILD" \
  -project "$IOS_ROOT/PersonalMythForge.xcodeproj" \
  -scheme "PersonalMythForge" \
  -destination "generic/platform=iOS" \
  -derivedDataPath "$DERIVED_DATA_PATH" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  build
