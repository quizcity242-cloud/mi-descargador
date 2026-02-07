import os
import traceback
import subprocess
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from static_ffmpeg import add_paths

# Intentamos activar FFmpeg
add_paths()

app = Flask(__name__)
DOWNLOAD_FOLDER = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No llegó el link"}), 400
    
    url = data['url']
    print(f"DEBUG: Intentando descarga extrema: {url}")

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'noplaylist': True,
        'quiet': False,
        # Headers ultra-reales para confundir al sitio
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Extraemos info
            info = ydl.extract_info(url, download=True)
            # 2. Obtenemos el nombre real del archivo generado
            filename = ydl.prepare_filename(info)
            
            print(f"DEBUG: ¡ÉXITO! Enviando: {filename}")
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        print("--- ERROR REAL DETECTADO (Copia esto) ---")
        # Esto imprimirá el error técnico real en los logs de Render
        error_msg = str(e)
        traceback.print_exc() 
        return jsonify({"error": f"Error técnico: {error_msg[:100]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


