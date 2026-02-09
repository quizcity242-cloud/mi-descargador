import os
import traceback
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
from static_ffmpeg import add_paths

# Activamos el motor de video
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

    print(f"DEBUG: Iniciando petición para: {url}")
    
    # Configuración limpia para evitar el AssertionError
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,
        'no_warnings': True,
        # Usamos el archivo de cookies si existe
        'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
        # Un User-Agent de Chrome moderno y estándar
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraer e iniciar descarga
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            print(f"DEBUG: Descarga exitosa: {filename}")
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        error_msg = str(e)
        print("--- ERROR EN DESCARGA ---")
        traceback.print_exc()
        
        # Respuesta amigable según el error
        if "confirm you're not a bot" in error_msg.lower():
            return jsonify({"error": "Bloqueo de Bot detectado. Prueba con otro sitio o actualiza tus cookies."}), 500
        return jsonify({"error": f"Error: {error_msg[:100]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
  




