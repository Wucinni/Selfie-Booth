import tkinter as tk
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

fullscreen_status = False
width_constant = 0.46875
changed_video_location_status = False


def check_fullscreen():
    global fullscreen_status
    if fullscreen_status:
        root.attributes('-fullscreen', True)

    else:
        root.attributes('-fullscreen', False)
    root.after(50, check_fullscreen)


def fullscreen():
    global fullscreen_status
    while True:
        keyboard.wait("x")

        if not fullscreen_status:
            fullscreen_status = True
            emptyMenu = Menu(root)
            root.config(menu=emptyMenu)
            print("Fullscreen")
        else:
            fullscreen_status = False
            print("Windowed")
            root.config(menu=menubar)


def video():
    global changed_video_location_status
    while True:
        path = settings.get_videos_folder()
        files = os.listdir(path)
        video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
        latest_video = None
        frame_data = None

        latest_video = video_files[0]
        frame_data = imageio.get_reader(path + "/" + latest_video)


        if frame_data is not None:
            for frame in frame_data.iter_data():
                if changed_video_location_status:
                    changed_video_location_status = False
                    break
                frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((int(root.winfo_width() * width_constant), root.winfo_height())))
                middle_container.config(image=frame_image)
                middle_container.image = frame_image

                qr_size = int(0.3 * root.winfo_width() * width_constant)

                qr_frame_left = ImageTk.PhotoImage(Image.fromarray(np.array(generate_qr.generate_qr_code(f"http://{settings.get_server_ip()}:{settings.get_server_port()}"))).resize((qr_size, qr_size), resample=Image.LANCZOS))
                left_container.config(image=qr_frame_left)
                left_container.image = qr_frame_left

                qr_frame_right = ImageTk.PhotoImage(Image.fromarray(np.array(generate_qr.generate_qr_wifi(settings.get_wifi_ssid(), settings.get_wifi_password()))).resize((qr_size, qr_size), resample=Image.LANCZOS))
                right_container.config(image=qr_frame_right)
                right_container.image = qr_frame_right


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
    settings.set_videos_folder(videos_directory)
    if not render_video_thread.is_alive():
        render_video_thread = Thread(target=video)
        render_video_thread.daemon = 1
        render_video_thread.start()
    changed_video_location_status = True


def save_wifi_credentials():
    settings.set_wifi_ssid(wifi_ssid.get())
    settings.set_wifi_password(wifi_password.get())
    wifi_input_box.destroy()
    messagebox.showinfo(title="Confirmation Box", message="Wifi credentials saved")


def set_wifi_credentials():
    global wifi_ssid, wifi_password, wifi_input_box
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

    save_button = tk.Button(wifi_input_box, text="Save", command=save_wifi_credentials)
    save_button.pack()


# Submenu
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Start Server", command=start_server_thread)
filemenu.add_command(label="Video Directory", command=set_videos_location)
filemenu.add_command(label="Wifi", command=set_wifi_credentials)
menubar.add_cascade(label="Menu", menu=filemenu)
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
render_video_thread = Thread(target=video)
render_video_thread.daemon = 1
render_video_thread.start()

fullscreen_thread = Thread(target=fullscreen)
fullscreen_thread.daemon = 1
fullscreen_thread.start()

check_fullscreen()

root.mainloop()


