from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import os
from yt_dlp import YoutubeDL
import logging
import traceback
import re

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
logging.basicConfig(level=logging.DEBUG)

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url')
        format = data.get('format')
        
        if not url or not format:
            return jsonify({'error': 'URL and format are required'}), 400

        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'no_warnings': True,
            'quiet': True,
            # Add these options to bypass age restriction and reduce errors
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': True,
            'extract_flat': False,
            'youtube_include_dash_manifest': False,
            # Add cookies and headers to appear more like a browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

        if format == 'mp3':
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info['title']
                safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
                
                if format == 'mp3':
                    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp3")
                else:
                    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")

                if not os.path.exists(file_path):
                    files = os.listdir(DOWNLOAD_DIR)
                    for file in files:
                        if file.endswith(f".{format}"):
                            file_path = os.path.join(DOWNLOAD_DIR, file)
                            break

                if not os.path.exists(file_path):
                    return jsonify({'error': 'Downloaded file not found'}), 500

                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=f"{safe_title}.{format}",
                    mimetype=f'{"audio" if format == "mp3" else "video"}/{format}'
                )

        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({'error': f'Error downloading: {str(e)}'}), 500

    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))