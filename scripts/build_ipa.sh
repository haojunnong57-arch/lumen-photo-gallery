#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APP_NAME="Lumen"
SCHEME="Lumen"
BUILD_DIR="build"
ARCHIVE_DIR="$BUILD_DIR/$APP_NAME.xcarchive"
EXPORT_DIR="$BUILD_DIR/export"
IPA_PATH="$BUILD_DIR/$APP_NAME.ipa"

echo "==> Generate project"
if ! command -v xcodegen >/dev/null 2>&1; then
  echo "xcodegen not found: brew install xcodegen" >&2
  exit 1
fi
xcodegen generate

echo "==> Archive (Release, unsigned)"
rm -rf "$ARCHIVE_DIR" "$EXPORT_DIR" "$IPA_PATH"
mkdir -p "$BUILD_DIR"
xcodebuild \
  -project "$APP_NAME.xcodeproj" \
  -scheme "$SCHEME" \
  -configuration Release \
  -destination 'generic/platform=iOS' \
  -archivePath "$ARCHIVE_DIR" \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO \
  CODE_SIGN_IDENTITY="" \
  archive

echo "==> Package Payload"
APP_PATH="$ARCHIVE_DIR/Products/Applications/$APP_NAME.app"
if [ ! -d "$APP_PATH" ]; then
  echo "App not found at $APP_PATH" >&2
  exit 1
fi
mkdir -p "$EXPORT_DIR/Payload"
cp -R "$APP_PATH" "$EXPORT_DIR/Payload/"
(cd "$EXPORT_DIR" && /usr/bin/zip -qry "$APP_NAME.ipa" Payload)
mv "$EXPORT_DIR/$APP_NAME.ipa" "$IPA_PATH"

echo "==> Done: $IPA_PATH"
shasum -a 256 "$IPA_PATH"
