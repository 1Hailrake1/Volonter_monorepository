#!/bin/bash
set -e

echo "🔑 Generating new JWT keys..."
python -c "from app.security.generate_jwt_keys import generate_jwt_keys; generate_jwt_keys()"

echo "✅ JWT keys generated successfully"
echo "🚀 Starting application with $@ workers..."

# Запуск приложения с переданными аргументами
exec "$@"
