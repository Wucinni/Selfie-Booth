import tkinter as tk
import time
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import imageio
from PIL import Image, ImageTk
import generate_qr
from threading import Thread
import keyboard
import numpy as np
import os
import settings
import flask_server
from moviepy.editor import VideoFileClip

fullscreen_status = False
width_constant = 0.46875
changed_video_location_status = False


def make_window_fullscreen():
    root.attributes('-fullscreen', True) if fullscreen_status else root.attributes('-fullscreen', False)
    root.after(50, make_window_fullscreen)


def set_fullscreen_variable():
    global fullscreen_status
    while True:
        keyboard.wait("x")

        if not fullscreen_status:
            fullscreen_status = True
            empty_menu = Menu(root)
            root.config(menu=empty_menu)
        else:
            fullscreen_status = False
            root.config(menu=menubar)


def play_video():
    global changed_video_location_status
    while True:
        path = settings.get_videos_folder()
        files = os.listdir(path)
        video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)

        latest_video = video_files[0]
        frame_data = imageio.get_reader(path + "/" + latest_video)
        frame_rate = frame_data.get_meta_data()['fps']  # Get the original frame rate of the video

        video_clip = VideoFileClip(path + "/" + latest_video)
        audio_clip = video_clip.audio
        audio_thread = Thread(target=audio_clip.preview)

        if frame_data is not None:
            if audio_state == "On":
                audio_thread.daemon = True
                audio_thread.start()

            start_time = time.time()  # Get the start time
            for frame_number, frame in enumerate(frame_data.iter_data()):
                if changed_video_location_status:
                    changed_video_location_status = False
                    break

                frame_time = frame_number / frame_rate  # Calculate the time stamp of the frame
                elapsed_time = time.time() - start_time  # Calculate the elapsed time
                remaining_time = frame_time - elapsed_time  # Calculate the remaining time until the frame should be displayed

                if remaining_time > 0:
                    time.sleep(remaining_time)  # Wait until it's time to display the frame

                frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((int(root.winfo_width() * width_constant), root.winfo_height())))
                middle_container.config(image=frame_image)
                middle_container.image = frame_image

                qr_size = int(0.3 * root.winfo_width() * width_constant)

                qr_frame_right = ImageTk.PhotoImage(Image.fromarray(np.array(generate_qr.generate_qr_code(f"http://{settings.get_server_ip()}:{settings.get_server_port()}"))).resize((qr_size, qr_size), resample=Image.LANCZOS))
                right_container.config(image=qr_frame_right)
                right_container.image = qr_frame_right

                qr_frame_left = ImageTk.PhotoImage(Image.fromarray(np.array(generate_qr.generate_qr_wifi(settings.get_wifi_ssid(), settings.get_wifi_password()))).resize((qr_size, qr_size), resample=Image.LANCZOS))
                left_container.config(image=qr_frame_left)
                left_container.image = qr_frame_left
            print(time.time() - start_time)


settings.set_default_settings()
# Main window
root = tk.Tk()
root.title("360 Gallery")
# root.wm_attributes('-toolwindow', 'True')
root.geometry("600x599")
window_width = root.winfo_width()
window_height = root.winfo_height()


def start_server_thread():
    server_thread = Thread(target=flask_server.run)
    server_thread.daemon = 1
    server_thread.start()
    messagebox.showinfo(title="Confirmation Box", message="Server was started")


def set_videos_location():
    global render_video_thread, changed_video_location_status
    videos_directory = filedialog.askdirectory()
    if len(videos_directory) > 0:
        settings.set_videos_folder(videos_directory)
    if not render_video_thread.is_alive():
        render_video_thread = Thread(target=play_video)
        render_video_thread.daemon = 1
        render_video_thread.start()
    changed_video_location_status = True


def save_wifi_credentials(wifi_input_box, ssid, password):
    settings.set_wifi_ssid(ssid)
    settings.set_wifi_password(password)
    wifi_input_box.destroy()
    messagebox.showinfo(title="Confirmation Box", message="Wifi credentials saved")


def save_ip(ip_input_box, ip):
    settings.set_server_ip(ip)
    ip_input_box.destroy()
    messagebox.showinfo(title="Confirmation Box", message="IP saved")

def set_local_ip():
    ip_input_box = tk.Toplevel(root)
    ip_input_box.title("Enter local IP")

    ip_label = tk.Label(ip_input_box, text="IP:")
    ip_label.pack()
    ip_ssid = tk.Entry(ip_input_box)
    ip_ssid.pack()

    save_button = tk.Button(ip_input_box, text="Save",
                            command=lambda: save_ip(ip_input_box, ip_ssid.get()))
    save_button.pack()


def save_port(port_input_box, port):
    settings.set_server_port(port)
    port_input_box.destroy()
    messagebox.showinfo(title="Confirmation Box", message="Port saved")

def set_port():
    port_input_box = tk.Toplevel(root)
    port_input_box.title("Enter port")

    port_label = tk.Label(port_input_box, text="Port:")
    port_label.pack()
    port_ssid = tk.Entry(port_input_box)
    port_ssid.pack()

    save_button = tk.Button(port_input_box, text="Save",
                            command=lambda: save_port(port_input_box, port_ssid.get()))
    save_button.pack()


def set_wifi_credentials():
    wifi_input_box = tk.Toplevel(root)
    wifi_input_box.title("Wifi Credentials")

    ssid_label = tk.Label(wifi_input_box, text="Wifi name:")
    ssid_label.pack()
    wifi_ssid = tk.Entry(wifi_input_box)
    wifi_ssid.pack()

    password_label = tk.Label(wifi_input_box, text="Password:")
    password_label.pack()
    wifi_password = tk.Entry(wifi_input_box)
    wifi_password.pack()

    save_button = tk.Button(wifi_input_box, text="Save",
                            command=lambda: save_wifi_credentials(wifi_input_box, wifi_ssid.get(), wifi_password.get()))
    save_button.pack()


def change_audio_state():
    global audio_state
    if audio_state == "On":
        audio_state = "Off"
    elif audio_state == "Off":
        audio_state = "On"

    menu.entryconfigure(3, label=f"Audio: {audio_state}")



audio_state = "Off"
# Submenu
menubar = Menu(root)
menu = Menu(menubar, tearoff=0)
server_menu = Menu(menu, tearoff=0)

menubar.add_cascade(label="Menu", menu=menu)
menu.add_cascade(label="Server", menu=server_menu)

server_menu.add_command(label="Start Server", command=start_server_thread)
server_menu.add_command(label="Save IP", command=set_local_ip)
server_menu.add_command(label="Save Port", command=set_port)
menu.add_command(label="Video Directory", command=set_videos_location)
menu.add_command(label="Wifi", command=set_wifi_credentials)
menu.add_command(label=f"Audio: {audio_state}", command=change_audio_state)

root.config(menu=menubar)

# Background
image = Image.open("templates/background.png").resize((1920, 1080))
image_array = Image.fromarray(np.array(image))
background_image = ImageTk.PhotoImage(image_array)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Containers
left_container = ttk.Label(root)
left_container.pack(side="left", expand=True,  padx=10)
left_qr = ImageTk.PhotoImage(generate_qr.generate_qr_wifi(settings.get_wifi_ssid(), settings.get_wifi_password()))
left_container.config(image=left_qr)

middle_container = ttk.Label(root)
middle_container.pack(side="left", expand=True, padx=10)

right_container = ttk.Label(root)
right_container.pack(side="left", expand=True,  padx=10)
right_qr = ImageTk.PhotoImage(generate_qr.generate_qr_code(f"http://{settings.get_server_ip()}:{settings.get_server_port()}"))
right_container.config(image=right_qr)


# Threads
render_video_thread = Thread(target=play_video)
render_video_thread.daemon = 1
render_video_thread.start()

fullscreen_thread = Thread(target=set_fullscreen_variable)
fullscreen_thread.daemon = 1
fullscreen_thread.start()

make_window_fullscreen()

root.mainloop()
