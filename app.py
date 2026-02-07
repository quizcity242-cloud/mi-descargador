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
    cookie_file = 'cookies.txt' # El archivo que subiste a GitHub

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'quiet': False,
        # Si el archivo existe, lo usa para saltar el bloqueo de bot
        'cookiefile': cookie_file if os.path.exists(cookie_file) else None,
        # Solución para Dailymotion (Disfraz de Firefox)
        'impersonate': 'firefox', 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        print("--- ERROR DETECTADO ---")
        traceback.print_exc()
        return jsonify({"error": f"Bloqueo detectado: {str(e)[:100]}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

