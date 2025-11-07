# /api/Dockerfile
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# instalar dependencias del sistema necesarias (ffmpeg para procesamiento)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# actualizar pip
RUN python -m pip install --upgrade pip

WORKDIR /app

# copiar requirements e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 🔹 Agregar argumento para invalidar cache de código
ARG CACHE_BUSTER=1

# copiar aplicación
COPY app.py /app/app.py
# Si tenés más módulos:
# COPY app/ /app/

# 🔹 Forzar actualización de timestamps (opcional, extra seguridad)
RUN find /app -type f -exec touch {} +

# crear carpeta de descargas con permisos adecuados
RUN mkdir -p /app/downloads && chmod 755 /app/downloads

# puerto que usa Flask (interno)
EXPOSE 5000

# usar gunicorn para producción
CMD ["gunicorn", "--workers", "2", "--timeout", "300", "--bind", "0.0.0.0:5000", "app:app"]