#!/bin/bash
set -e

# Create instance directory for SQLite DB
mkdir -p instance

# Auto-detect Codespaces URL for QR code generation
if [ -n "$CODESPACE_NAME" ]; then
    export SITE_URL="https://${CODESPACE_NAME}-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-preview.app.github.dev}"
    echo "SITE_URL set to $SITE_URL"
fi

cd car-sos
python app.py
