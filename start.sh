#!/bin/bash
set -e

# Build frontend if not already built
if [ ! -d "build" ]; then
    echo "Build directory not found. Building frontend..."
    bash scripts/build_frontend.sh
fi

# Set Flask app for CLI commands
export FLASK_APP=wsgi:app

# Run Flask database migrations
flask db upgrade

# Start Gunicorn with config file
# PORT is provided by Render/Heroku, fallback to 8000 for local
exec gunicorn wsgi:app \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout 120 \
    --log-file - \
    --access-logfile -
