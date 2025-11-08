#!/bin/sh
set -e

# Paso 1: Definir valor por defecto para desarrollo
: "${BACKEND_URL:=http://api:5000}"

# Paso 2: Generar config.js para el frontend
cat > /usr/share/nginx/html/js/config.js <<EOF
export const API_BASE_URL = "/api";
EOF

echo "✅ config.js generado"

# Paso 3: REEMPLAZAR la variable ${BACKEND_URL} en nginx.conf
envsubst '${BACKEND_URL}' < /etc/nginx/nginx.conf.prod > /etc/nginx/nginx.conf

echo "✅ nginx.conf generado con BACKEND_URL=${BACKEND_URL}"

# Paso 4: Iniciar nginx
exec "$@"