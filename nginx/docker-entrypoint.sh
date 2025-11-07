#!/bin/sh
set -e

# Valor por defecto si no se proporciona
: "${BACKEND_URL:=https://flask-yt-download.onrender.com}"

# Generar config.js con la URL del backend
cat > /usr/share/nginx/html/js/config.js <<EOF
const API_BASE_URL = "${BACKEND_URL}";
EOF

echo "✅ config.js generado con API_BASE_URL=${BACKEND_URL}"

# Iniciar nginx
exec "$@"