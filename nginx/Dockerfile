# /nginx/Dockerfile
FROM nginx:stable-alpine

# instalar envsubst (ya disponible en /bin/sh con apk)
RUN apk add --no-cache gettext

WORKDIR /usr/share/nginx/html

# 🔹 Paso 1: variable "dummy" que siempre invalida la cache de Docker
# (cada vez que cambies su valor, Render rehace completamente la capa)
ARG CACHE_BUSTER=1

# 🔹 Paso 2: copiar el frontend estático
COPY web/ /usr/share/nginx/html/

# 🔹 Paso 3: forzar actualización de timestamps (garantiza reempaquetado)
RUN find /usr/share/nginx/html -type f -exec touch {} +

# Copiar plantilla nginx
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# ENTRYPOINT: al iniciar, reemplazamos la variable y ejecutamos nginx en foreground
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
