import os
import traceback
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from static_ffmpeg import add_paths

# Activamos el motor de video FFmpeg
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
    print(f"DEBUG: Intentando descargar: {url}")

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'noplaylist': True,
        'quiet': False,
        # ESTA ES LA LÍNEA CLAVE: Desactiva el disfraz que causa el error
        'extractor_args': {'dailymotion': {'impersonate': ['']}},
        # Usamos un User-Agent estándar de Chrome
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"DEBUG: Archivo descargado en el servidor: {filename}")
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        print("--- LOG DE ERROR ---")
        traceback.print_exc()
        return jsonify({"error": "Dailymotion bloqueó el acceso. Intenta con un link de MissAV o Youtube para probar."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)






