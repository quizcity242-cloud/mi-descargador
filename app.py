import os
import traceback
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
    # Ruta absoluta para evitar confusiones
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')

    print("--- INICIO DE DIAGNÓSTICO ---")
    if os.path.exists(cookie_path):
        size = os.path.getsize(cookie_path)
        print(f"DEBUG: Archivo cookies.txt encontrado. Tamaño: {size} bytes")
        # Leemos la primera línea para verificar el formato
        with open(cookie_path, 'r') as f:
            first_line = f.readline().strip()
            print(f"DEBUG: Primera línea de cookies: {first_line[:50]}...")
    else:
        print("DEBUG: ¡ERROR! El archivo cookies.txt NO EXISTE en el servidor.")
    print("----------------------------")

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,
        'cookiefile': cookie_path if os.path.exists(cookie_path) else None,
        # Probamos sin impersonate primero para YouTube, es más estable con cookies
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    # Si es Dailymotion, activamos el disfraz especial
    if 'dailymotion' in url.lower():
        ydl_opts['impersonate'] = 'firefox'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        error_msg = str(e)
        print("--- ERROR TÉCNICO DETECTADO ---")
        traceback.print_exc()
        # Si el error contiene "confirm you're not a bot", es que las cookies fallaron
        if "confirm you're not a bot" in error_msg.lower():
            return jsonify({"error": "YouTube detectó un bot. Tus cookies podrían ser inválidas o viejas."}), 500
        return jsonify({"error": f"Fallo: {error_msg[:100]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


