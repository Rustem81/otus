#!/bin/sh
set -e

echo "Generating runtime config..."

API_URL="${API_URL:-http://localhost:8000}"

# Create config.js in /tmp (writable location)
cat > /tmp/config.js << EOF
window.__appConfig = {
  API_URL: '${API_URL}',
  CONFIG_SOURCE: 'runtime',
  CONFIG_GENERATED_AT: '$(date -Iseconds)'
};
EOF

echo "Runtime config created:"
cat /tmp/config.js

echo "Starting nginx..."
exec "$@"
