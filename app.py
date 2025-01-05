from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import os
from pytube import YouTube
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

        try:
            yt = YouTube(url)
            video_title = yt.title
            safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
            
            if format == 'mp3':
                # Get audio stream
                stream = yt.streams.filter(only_audio=True).first()
                if not stream:
                    return jsonify({'error': 'No audio stream available'}), 400
                
                # Download as MP4 first
                file_path = stream.download(DOWNLOAD_DIR, filename=f"{safe_title}.mp4")
                
                # Convert to MP3
                base, _ = os.path.splitext(file_path)
                new_file_path = base + '.mp3'
                os.rename(file_path, new_file_path)
                file_path = new_file_path
                
            else:
                # Get video stream
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
                if not stream:
                    return jsonify({'error': 'No video stream available'}), 400
                
                file_path = stream.download(DOWNLOAD_DIR, filename=f"{safe_title}.mp4")

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