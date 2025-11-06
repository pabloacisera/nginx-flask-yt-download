# /nginx/Dockerfile
FROM nginx:stable-alpine

# instalar envsubst (ya disponible en /bin/sh con apk)
RUN apk add --no-cache gettext

WORKDIR /usr/share/nginx/html

# Copiar frontend estático
COPY web/ /usr/share/nginx/html/

# Copiar plantilla nginx
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# ENTRYPOINT: al iniciar, reemplazamos la variable y ejecutamos nginx en foreground
# El script se encarga de reemplazar {{BACKEND_URL}} por la variable de entorno BACKEND_URL
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
