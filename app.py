import os
import traceback
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    print(f"DEBUG: Intentando descargar: {url}") # Esto saldrá en tus logs

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-s', '16', '-k', '1M'],
        'impersonate': 'chrome',
        'extractor_args': {'generic': ['impersonate']},
        'nocheckcertificate': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"DEBUG: Descarga exitosa: {filename}")
            return send_file(filename, as_attachment=True)
    except Exception as e:
        print("--- ERROR DETECTADO ---")
        traceback.print_exc() # Esto me dirá la línea exacta del error
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
