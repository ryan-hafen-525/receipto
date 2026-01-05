#!/bin/bash
set -e

# Fix permissions on the mounted volume
# This runs as root before switching to appuser
if [ -d "/app/storage" ]; then
    echo "Fixing storage directory permissions..."
    chown -R appuser:appuser /app/storage
    chmod -R 755 /app/storage
fi

# Execute the CMD as appuser
exec "$@"
