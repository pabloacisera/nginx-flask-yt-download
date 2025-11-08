#!/bin/sh
set -e

# Valor por defecto si no se proporciona
: "${BACKEND_URL:=/api}"

# Generar config.js con la URL del backend
cat > /usr/share/nginx/html/js/config.js <<EOF
export const API_BASE_URL = "${BACKEND_URL}";
EOF

echo "✅ config.js generado con API_BASE_URL=${BACKEND_URL}"

# ✅ Copiar nginx.conf.template a nginx.conf
cp /etc/nginx/nginx.conf.template /etc/nginx/nginx.conf
echo "✅ nginx.conf copiado desde template"

# Iniciar nginx
exec "$@"