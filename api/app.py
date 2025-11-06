# app/app.py

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
from yt_dlp import YoutubeDL
import traceback
import subprocess  # Para ejecutar comandos FFmpeg

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configuración de yt-dlp SOLO para extraer información (sin descargar)
YTDL_INFO_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'skip_download': True,
}

# Configuración de yt-dlp para descargar y convertir
YTDL_DOWNLOAD_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'quiet': False,
    'no_warnings': False,
}

@app.route('/api/search', methods=['POST'])
def search_video():
    """
    Endpoint para buscar y extraer información de un video.
    NO descarga el archivo, solo obtiene los metadatos.
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'Falta campo url en la petición'
        }), 400
    
    url = data['url']
    
    if not url.startswith(('http://', 'https://')):
        return jsonify({
            'success': False,
            'error': 'URL inválida. Debe empezar con http:// o https://'
        }), 400
    
    print(f"[INFO] Extrayendo información de: {url}")
    
    try:
        with YoutubeDL(YTDL_INFO_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            
            print(f"[INFO] Información extraída: {info.get('title', 'Sin título')}")
            
            video_id = info.get('id', 'unknown')
            video_title = info.get('title', 'Desconocido')
            uploader = info.get('uploader', 'Desconocido')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', '')
            view_count = info.get('view_count', 0)
            upload_date = info.get('upload_date', '')
            
            audio_quality = 'Desconocida'
            audio_bitrate = 'Desconocido'
            audio_codec = 'Desconocido'
            
            if 'formats' in info:
                audio_formats = [
                    f for f in info['formats'] 
                    if f.get('acodec') != 'none' and f.get('vcodec') == 'none'
                ]
                
                if audio_formats:
                    audio_formats.sort(
                        key=lambda x: x.get('abr', 0) or 0, 
                        reverse=True
                    )
                    best_audio = audio_formats[0]
                    
                    audio_bitrate = best_audio.get('abr', 'Desconocido')
                    audio_codec = best_audio.get('acodec', 'Desconocido')
                    
                    if isinstance(audio_bitrate, (int, float)):
                        if audio_bitrate >= 256:
                            audio_quality = "Alta (≥256 kbps)"
                        elif audio_bitrate >= 128:
                            audio_quality = "Media (128-256 kbps)"
                        else:
                            audio_quality = f"Básica ({audio_bitrate} kbps)"
            
            duration_formatted = f"{duration // 60}:{duration % 60:02d}" if duration else "Desconocida"
            
            estimated_size = 0
            if isinstance(audio_bitrate, (int, float)) and duration:
                estimated_size = round((audio_bitrate * duration) / 8 / 1024, 2)
            
            response_data = {
                'success': True,
                'video_id': video_id,
                'metadata': {
                    'title': video_title,
                    'artist': uploader,
                    'duration': duration_formatted,
                    'duration_seconds': duration,
                    'thumbnail': thumbnail,
                    'views': view_count,
                    'upload_date': upload_date,
                },
                'audio_info': {
                    'quality': audio_quality,
                    'bitrate': f"{audio_bitrate} kbps" if isinstance(audio_bitrate, (int, float)) else audio_bitrate,
                    'codec': audio_codec,
                    'format': 'MP3',
                    'target_quality': '320 kbps',
                    'estimated_size_mb': estimated_size,
                },
                'download_endpoint': f'/api/download/{video_id}',
                'download_enhanced_endpoint': f'/api/download/{video_id}/enhanced',
                'note': 'La descarga comenzará cuando hagas clic en el botón de descarga.'
            }
            
            return jsonify(response_data), 200
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[ERROR] Error al extraer información:")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': 'Error al extraer información del video',
            'details': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    """
    Endpoint para descargar el MP3 original (sin mejoras).
    """
    print(f"[INFO] Iniciando descarga ORIGINAL de video ID: {video_id}")
    
    filename = f"{video_id}.mp3"
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    
    # Si ya existe, lo servimos directamente
    if os.path.exists(filepath):
        print(f"[INFO] Archivo original ya existe, sirviéndolo: {filename}")
        return send_file(filepath, as_attachment=True, download_name=filename)
    
    # Si no existe, lo descargamos
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        print(f"[INFO] Descargando y convirtiendo: {url}")
        
        with YoutubeDL(YTDL_DOWNLOAD_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            
            print(f"[INFO] Descarga original completada: {filename}")
            
            if os.path.exists(filepath):
                file_size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)
                print(f"[INFO] Sirviendo archivo original: {filename} ({file_size_mb} MB)")
                
                return send_file(
                    filepath, 
                    as_attachment=True, 
                    download_name=f"{info.get('title', video_id)}.mp3"
                )
            else:
                raise FileNotFoundError("El archivo no se generó correctamente")
                
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[ERROR] Error en la descarga original:")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': 'Error al descargar el archivo',
            'details': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/download/<video_id>/enhanced', methods=['GET'])
def download_video_enhanced(video_id):
    """
    Endpoint para descargar el MP3 mejorado con procesamiento FFmpeg.
    
    Proceso:
    1. Verifica si existe el archivo mejorado (caché)
    2. Si no existe, descarga el original
    3. Procesa con FFmpeg (normalización, EQ, compresión)
    4. Sirve el archivo mejorado
    """
    print(f"[INFO] Iniciando descarga MEJORADA de video ID: {video_id}")
    
    # Nombres de archivo
    original_filename = f"{video_id}.mp3"
    enhanced_filename = f"{video_id}_enhanced.mp3"
    original_filepath = os.path.join(DOWNLOAD_DIR, original_filename)
    enhanced_filepath = os.path.join(DOWNLOAD_DIR, enhanced_filename)
    
    try:
        # Paso 1: Verificar si ya existe el archivo mejorado (caché)
        if os.path.exists(enhanced_filepath):
            print(f"[INFO] Archivo mejorado ya existe (caché), sirviéndolo: {enhanced_filename}")
            file_size_mb = round(os.path.getsize(enhanced_filepath) / (1024 * 1024), 2)
            print(f"[INFO] Tamaño archivo mejorado: {file_size_mb} MB")
            return send_file(enhanced_filepath, as_attachment=True, download_name=enhanced_filename)
        
        # Paso 2: Descargar el original si no existe
        if not os.path.exists(original_filepath):
            print(f"[INFO] Archivo original no existe, descargando primero...")
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            with YoutubeDL(YTDL_DOWNLOAD_OPTS) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"[INFO] Descarga original completada para procesamiento")
        else:
            print(f"[INFO] Archivo original ya existe, procediendo a mejorar")
        
        # Paso 3: Procesar con FFmpeg
        print(f"[INFO] Iniciando procesamiento FFmpeg...")
        
        # Comando FFmpeg con filtros de mejora
        ffmpeg_command = [
            'ffmpeg',
            '-i', original_filepath,  # Archivo de entrada
            '-af', (  # Filtros de audio
                'loudnorm=I=-16:TP=-1.5:LRA=11,'  # Normalización de volumen
                'equalizer=f=100:t=q:w=1:g=2,'     # Realce de graves
                'equalizer=f=3000:t=q:w=1:g=1.5,'  # Realce de agudos
                'acompressor=threshold=0.5:ratio=2:attack=5:release=50'  # Compresión
            ),
            '-b:a', '320k',  # Bitrate de salida
            '-ar', '48000',  # Sample rate
            '-y',  # Sobrescribir si existe
            enhanced_filepath  # Archivo de salida
        ]
        
        # Ejecutar FFmpeg
        print(f"[INFO] Ejecutando: {' '.join(ffmpeg_command)}")
        result = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # Timeout de 5 minutos
        )
        
        # Verificar si FFmpeg tuvo éxito
        if result.returncode != 0:
            print(f"[ERROR] FFmpeg falló con código: {result.returncode}")
            print(f"[ERROR] stderr: {result.stderr}")
            raise Exception(f"FFmpeg falló: {result.stderr}")
        
        print(f"[INFO] Procesamiento FFmpeg completado exitosamente")
        
        # Paso 4: Verificar que el archivo mejorado existe
        if not os.path.exists(enhanced_filepath):
            raise FileNotFoundError("El archivo mejorado no se generó correctamente")
        
        # Obtener información del archivo mejorado
        file_size_mb = round(os.path.getsize(enhanced_filepath) / (1024 * 1024), 2)
        print(f"[INFO] Sirviendo archivo mejorado: {enhanced_filename} ({file_size_mb} MB)")
        
        # Paso 5: Servir el archivo mejorado
        return send_file(
            enhanced_filepath, 
            as_attachment=True, 
            download_name=enhanced_filename
        )
        
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Timeout en el procesamiento FFmpeg")
        return jsonify({
            'success': False,
            'error': 'Timeout en el procesamiento de audio',
            'details': 'El procesamiento tardó demasiado tiempo'
        }), 500
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[ERROR] Error en la descarga mejorada:")
        print(error_trace)
        
        return jsonify({
            'success': False,
            'error': 'Error al procesar el archivo mejorado',
            'details': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/health')
def health():
    """
    Endpoint de salud para verificar que la API está funcionando.
    """
    return jsonify({
        'status': 'ok',
        'message': 'API funcionando correctamente'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)