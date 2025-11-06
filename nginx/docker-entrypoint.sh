#!/bin/sh
set -e

# Si BACKEND_URL no está seteado, definimos un fallback (evita errores)
: "${BACKEND_URL:=http://127.0.0.1:5000/}"

# Reemplazar placeholder en la plantilla
# Nota: usamos envsubst para variables de entorno, pero nginx.conf.template usa {{BACKEND_URL}}, así que reemplazamos manualmente.
sed "s|{{BACKEND_URL}}|${BACKEND_URL}|g" /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Si necesitás construir un config.js con la API URL para el frontend:
if [ -d /usr/share/nginx/html/js ]; then
  echo "const API_BASE_URL = \"${BACKEND_URL}\";" > /usr/share/nginx/html/js/config.js
else
  mkdir -p /usr/share/nginx/html/js
  echo "const API_BASE_URL = \"${BACKEND_URL}\";" > /usr/share/nginx/html/js/config.js
fi

# Ejecutar comando por defecto (nginx)
exec "$@"
