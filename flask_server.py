from flask import Flask, send_from_directory, render_template
import os
import settings


app = Flask(__name__, static_folder='templates')
path = settings.get_videos_folder()


@app.route('/download')
def download_file():
    files = os.listdir(path)
    video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
    if not video_files:
        return "No video files found."

    # Video sorting by descending time
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    latest_video = video_files[0]

    return send_from_directory(path, latest_video)


@app.route('/')
def greeting():
    return render_template('landing.html')


def run():
    settings.set_default_settings()
    app.run(host=settings.get_server_ip(), port=int(settings.get_server_port()), debug=False)
