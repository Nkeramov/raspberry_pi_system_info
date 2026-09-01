#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_ROOT" || exit 1

set -a
source .env
set +a

if [ -z "$PORT" ]; then
    echo "Error: PORT is not set in .env"
    exit 1
fi

# Start the application
uv run gunicorn --bind 0.0.0.0:${PORT} 'src.rpi_system_info.app:create_app()'
