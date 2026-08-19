#!/usr/bin/env bash
set -e

# Apply database migrations, then start the server.
flask db upgrade || echo "No migrations to apply yet."

if [ "$FLASK_ENV" = "production" ]; then
    exec gunicorn --bind 0.0.0.0:5000 --workers 3 "app:create_app()"
else
    exec flask run --host 0.0.0.0 --port 5000
fi
