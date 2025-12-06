#!/bin/bash

# Exit on error
set -e

echo "🚀 Start building Antigravity Manager (macOS)..."

# 1. Sync resource files
echo "📦 Syncing resource files..."
# Ensure gui/assets directory exists
mkdir -p gui/assets
# Sync assets content to gui/assets
cp -R assets/* gui/assets/
# Sync requirements.txt
cp requirements.txt gui/requirements.txt

# 2. Clean old builds
echo "🧹 Cleaning old build files..."
rm -rf gui/build/macos

# 3. Execute build
echo "🔨 Start compiling..."
source .venv/bin/activate
cd gui

# Temporarily disable set -e, as flet build might throw SystemExit: 0 traceback but build actually succeeds
set +e

# Ensure no interactive mode
unset PYTHONINSPECT

# Use python -c to call flet_cli directly, bypassing potential entry point issues, and redirect input
python -c "import sys; from flet.cli import main; main()" build macos \
    --product "Antigravity Manager" \
    --org "com.ctrler.antigravity" \
    --copyright "Copyright (c) 2025 Ctrler" \
    --build-version "1.0.0" \
    --desc "Antigravity Account Manager Tool" < /dev/null
EXIT_CODE=$?
set -e

# Return to root directory
cd ..

# 4. Check build artifacts and package DMG
APP_NAME="Antigravity Manager"
APP_PATH="gui/build/macos/$APP_NAME.app"
DMG_NAME="$APP_NAME.dmg"
OUTPUT_DMG="gui/build/macos/$DMG_NAME"

if [ -d "$APP_PATH" ]; then
    echo "✅ App bundle detected, build successful (ignore Flet CLI exit status)"
else
    echo "❌ Build failed, app bundle not found"
    exit $EXIT_CODE
fi

echo "📦 Creating DMG installer..."

# Create temp directory for DMG creation
DMG_SOURCE="gui/build/macos/dmg_source"
rm -rf "$DMG_SOURCE"
mkdir -p "$DMG_SOURCE"

# Copy app to temp directory
echo "📋 Copying app to temp directory..."
cp -R "$APP_PATH" "$DMG_SOURCE/"

# Create Applications symlink
ln -s /Applications "$DMG_SOURCE/Applications"

# Use hdiutil to create DMG
echo "💿 Creating DMG file..."
rm -f "$OUTPUT_DMG"
TEMP_DMG="gui/build/macos/temp.dmg"
rm -f "$TEMP_DMG"

# Step 1: Create read-write DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_SOURCE" -ov -format UDRW "$TEMP_DMG"

# Step 2: Convert to compressed read-only DMG
hdiutil convert "$TEMP_DMG" -format UDZO -o "$OUTPUT_DMG"

# Cleanup
rm -f "$TEMP_DMG"
rm -rf "$DMG_SOURCE"

echo "🎉 Packaging complete!"
echo "📂 App location: $APP_PATH"
echo "💿 DMG file: $OUTPUT_DMG"
