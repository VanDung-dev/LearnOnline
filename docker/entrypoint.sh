#!/bin/sh

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Load sample data
echo "Loading sample data..."
python scripts/load_sample_data.py

# Start server
echo "Starting server"
exec "$@"