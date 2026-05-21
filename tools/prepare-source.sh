#!/usr/bin/env bash
# Prepare a staging directory that merges guidebook submodule content with
# production navigation files. This is temporary until index.md files are
# merged into the guidebook repository; at that point this script and the
# nav/ directory can be removed.
set -euo pipefail

STAGING="_staging"

rm -rf "$STAGING"
mkdir -p "$STAGING"

# Copy guidebook submodule content
cp -r guidebook/* "$STAGING/"

# Overlay Sphinx navigation files
cp -r nav/* "$STAGING/"

echo "Staging directory prepared at $STAGING/"
