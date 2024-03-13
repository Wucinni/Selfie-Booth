from flask import Flask, send_from_directory, render_template, request
import os
import settings


app = Flask(__name__, static_folder='templates')
settings.set_default_settings()
path = settings.get_videos_folder()
video_files = []


@app.route('/download')
def return_video():
    global video_files
    files = os.listdir(path)
    video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
    if not video_files:
        return "No video files found."

    # Video sorting by descending time
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    position = int(request.args.get('index')[0])  # Retrieve the index parameter from the URL

    # Ensure the position is within the range of available video files
    if position < 0 or position >= len(video_files):
        return "Invalid video position."

    video_file = video_files[position]
    return send_from_directory(path, video_file)


@app.route('/video')
def video():
    global video_files
    if not video_files:
        return "No video files found."

    action = request.args.get('command')
    current_index = int(request.args.get('index')[0])

    if action == "next":
        next_index = current_index + 1
        if next_index < 0 or next_index >= len(video_files):
            next_index = current_index
            next_video = video_files[current_index]
            return render_template('landing.html', video_file=next_video, index=next_index)

        next_video = video_files[next_index]
        return render_template('landing.html', video_file=next_video, index=next_index)

    elif action == "last":
        previous_index = current_index - 1
        if previous_index < 0 or previous_index >= len(video_files):
            previous_index = current_index
            previous_video = video_files[current_index]
            return render_template('landing.html', video_file=previous_video, index=previous_index)

        previous_video = video_files[previous_index]
        return render_template('landing.html', video_file=previous_video, index=previous_index)

    return render_template('landing.html', index=0)


@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        UPLOAD_FOLDER = settings.get_videos_folder() + "/"
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        return 'File uploaded successfully'

    # Display a simple form for file upload
    return '''
        <!doctype html>
        <title>Upload File</title>
        <h2>Upload a File</h2>
        <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
        </form>
    '''


@app.route('/')
def greeting():
    return render_template('landing.html', index=0)


def run():
    settings.set_default_settings()
    app.run(host=settings.get_server_ip(), port=int(settings.get_server_port()), debug=False)
