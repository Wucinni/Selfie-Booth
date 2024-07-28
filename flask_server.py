#############################################
#                                           #
#  This script starts a simple Flask server #
#                                           #
#      It handles upload, download and      #
#              video playback               #
#                                           #
#############################################


from flask import Flask, send_from_directory, render_template, request
import os
import settings

app = Flask(__name__, static_folder='templates')

settings.set_default_settings()  # Write default settings to settings file in AppData
path = settings.get_settings("video_directory:")  # Get video directory from settings file
video_files = []


@app.route('/download')
def return_video():
    global video_files

    # Make a list of videos from video folder
    files = os.listdir(path)
    video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
    if not video_files:
        return "No video files found."

    # Sort videos by descending time
    video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)

    # Get video index in videos list
    position = int(request.args.get('index')[0])  # Retrieve the index parameter from the URL

    # Ensure that index is in range of videos
    if position < 0 or position >= len(video_files):
        return "Invalid video position."

    # Get current video
    video_file = video_files[position]

    # Use Flask built-in function to return the file
    return send_from_directory(path, video_file)


@app.route('/video')
def video():
    global video_files

    # Verify if videos exist in videos list
    if not video_files:
        return "No video files found."

    # Check if user wants next or previous video
    action = request.args.get('command')

    # Get the current index
    current_index = int(request.args.get('index')[0])

    if action == "next":
        # Increment index to get next video in list
        next_index = current_index + 1

        # Return current video if index is out of list(video doesn't exist)
        if next_index < 0 or next_index >= len(video_files):
            next_index = current_index
            next_video = video_files[current_index]
            return render_template('home.html', video_file=next_video, index=next_index)

        # Return next video
        next_video = video_files[next_index]
        return render_template('home.html', video_file=next_video, index=next_index)

    elif action == "last":
        # Decrement index to get previous video in list
        previous_index = current_index - 1

        # Return current video if index is out of list(video doesn't exist)
        if previous_index < 0 or previous_index >= len(video_files):
            previous_index = current_index
            previous_video = video_files[current_index]
            return render_template('home.html', video_file=previous_video, index=previous_index)

        # Return previous video
        previous_video = video_files[previous_index]
        return render_template('home.html', video_file=previous_video, index=previous_index)

    # In case of fail, return video at index 0
    return render_template('home.html', index=0)


@app.route('/<filename>')
def get_specific_video(filename):
    # Ensure the file exists in the video directory
    file_path = os.path.join(path, filename)
    if not os.path.isfile(file_path):
        return "Video file not found.", 404

    index = 0
    for position, video in enumerate(video_files):
        if filename == video:
            index = position

    print(index)

    # Render the template with the specific video file
    return render_template('home.html', video_file=filename, index=index)


@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    # Upload file on POST
    if request.method == 'POST':
        file = request.files['file']

        # Return error on missing file
        if file.filename == '':
            return 'No selected file'

        # Workaround for file upload to sensitive directories
        UPLOAD_FOLDER = path + "/"
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))  # Save file locally

        # Return success message
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
    # Return main page with video at index 0 (most recent video in the directory)
    return render_template('home.html', index=0)


def run():
    """
        Function starts the Flask server
        input - None
        output - None
    """
    # app = Flask(__name__, static_folder='templates')

    # Write default settings to settings file in case ip is missing
    settings.set_default_settings()

    # Start Flask server
    app.run(host=settings.get_settings("server_ip:"), port=int(settings.get_settings("server_port:")), debug=False,
            threaded=True)
