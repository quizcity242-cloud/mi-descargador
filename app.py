import os
import traceback
import time
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from static_ffmpeg import add_paths

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
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')

    print(f"DEBUG: Intentando descargar: {url}")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,
        'no_warnings': False,
        # Forzamos el uso del archivo de cookies
        'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
        # Añadimos un pequeño retraso para no parecer un bot veloz
        'sleep_interval': 1,
        'max_sleep_interval': 3,
        # User agent muy específico
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    # Configuración especial si NO es YouTube (Dailymotion/MissAV)
    if 'youtube' not in url.lower() and 'youtu.be' not in url.lower():
        ydl_opts['impersonate'] = 'firefox'
        ydl_opts['extractor_args'] = {'dailymotion': {'impersonate': ['firefox']}}

    try:
        # Esperamos un segundo antes de empezar
        time.sleep(1)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        error_msg = str(e)
        print("--- LOG DE ERROR ---")
        traceback.print_exc()
        
        # Sugerencia inteligente según el error
        if "confirm you're not a bot" in error_msg.lower():
            return jsonify({"error": "YouTube bloqueó la IP del servidor. ¡Intenta con el link de MissAV o Dailymotion ahora, que esos sí deberían dejarte!"}), 500
        
        return jsonify({"error": f"Fallo técnico: {error_msg[:100]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)



