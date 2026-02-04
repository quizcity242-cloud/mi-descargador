import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# En la nube (Render), solo podemos escribir en /tmp
DOWNLOAD_FOLDER = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL"}), 400

    # Configuración optimizada para servidores
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Descargar el video
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Enviarlo al usuario y luego borrarlo del servidor para no llenar espacio
            return send_file(filename, as_attachment=True)
            
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
