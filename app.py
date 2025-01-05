from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import logging
import traceback
from yt_dlp import YoutubeDL
import re

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
logging.basicConfig(level=logging.DEBUG)

# Create a permanent directory for downloads
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
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        url = data.get('url')
        format = data.get('format')
        
        app.logger.info(f"URL: {url}, Format: {format}")
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        if not format:
            return jsonify({'error': 'Format is required'}), 400

        try:
            # Clear old files in download directory
            for file in os.listdir(DOWNLOAD_DIR):
                try:
                    file_path = os.path.join(DOWNLOAD_DIR, file)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    app.logger.error(f"Error deleting old file {file}: {str(e)}")

            if format == 'mp3':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                    'extract_audio': True,
                    'audio_format': 'mp3',
                    'audio_quality': '192K',
                    'no_warnings': True,
                    'quiet': True
                }
            else:  # mp4
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                }

            app.logger.info("Starting download...")
            with YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=True)
                video_title = info['title']
                safe_title = re.sub(r'[<>:"/\\|?*]', '', video_title)
                
                if format == 'mp3':
                    # For MP3, we'll use the downloaded audio file directly
                    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.webm")
                    new_file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp3")
                    
                    # Rename the file to .mp3
                    if os.path.exists(file_path):
                        os.rename(file_path, new_file_path)
                        file_path = new_file_path
                else:
                    file_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp4")
                
                if not os.path.exists(file_path):
                    # If exact filename not found, try to find any mp3/mp4 file
                    files = os.listdir(DOWNLOAD_DIR)
                    for file in files:
                        if file.endswith(f".{format}"):
                            file_path = os.path.join(DOWNLOAD_DIR, file)
                            break
                
                if not os.path.exists(file_path):
                    return jsonify({'error': 'Downloaded file not found'}), 500

                try:
                    return send_file(
                        file_path,
                        as_attachment=True,
                        download_name=f"{safe_title}.{format}",
                        mimetype=f'{"audio" if format == "mp3" else "video"}/{format}'
                    )
                except Exception as e:
                    app.logger.error(f"Error sending file: {str(e)}")
                    return jsonify({'error': 'Error sending file'}), 500

        except Exception as e:
            app.logger.error(f"Error processing video: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({'error': f'Error processing video: {str(e)}'}), 500

    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)