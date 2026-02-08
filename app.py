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
    cookie_file = os.path.join(os.getcwd(), 'cookies.txt')

    # --- DIAGNÓSTICO DE COOKIES ---
    if os.path.exists(cookie_file):
        print(f"DEBUG: Archivo cookies.txt ENCONTRADO. Tamaño: {os.path.getsize(cookie_file)} bytes")
    else:
        print("DEBUG: ¡ALERTA! archivo cookies.txt NO ENCONTRADO en la raíz.")
    # ------------------------------

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        'impersonate': 'firefox', 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        full_error = str(e)
        print(f"--- ERROR TÉCNICO COMPLETO ---\n{full_error}")
        return jsonify({"error": f"Detalle: {full_error[:150]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

