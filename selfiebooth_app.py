#############################################
#                                           #
#  This script creates a GUI using Tkinter  #
#     The goal is to display 360 videos     #
#                                           #
#   It is also used to start a flask server #
#   It handles video frames and user input  #
#                                           #
#               MAIN MODULE                 #
#                                           #
#############################################


import flask_server
import generate_qr
import imageio
import keyboard
from moviepy.editor import VideoFileClip
import numpy as np
import os
from PIL import ImageTk
import PIL.Image
import psutil
import settings
import signal
from threading import Thread
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog


fullscreen_status = False
width_constant = 0.46875  # Constant multiplied with resolution to respect video aspect ratio; Change accordingly
changed_video_location_status = False  # Used to stop video when directory was changed
audio_state = "Off"  # Disable audio at app start


def make_window_fullscreen():
    """
        Function alternates fullscreen attribute between True and False
        input - None
        output - None
    """
    root.attributes('-fullscreen', True) if fullscreen_status else root.attributes('-fullscreen', False)
    root.after(50, make_window_fullscreen)


def set_fullscreen_variable():
    """
        This function handles keyboard input from user in order to change fullscreen flag
        input - None
        output - None
    """
    global fullscreen_status

    while True:
        keyboard.wait("f12")

        if not fullscreen_status:
            fullscreen_status = True
            # If window is set to fullscreen create an empty menu to hide the old one in the interface
            empty_menu = Menu(root)
            root.config(menu=empty_menu)
        else:
            fullscreen_status = False
            # If window is set to windowed set the old menu back in the interface
            root.config(menu=menubar)


def change_audio_state():
    """
        This function changes audio flag and modifies the entry in the Tkinter menu
        input - None
        output - None
    """
    global audio_state

    if audio_state == "On":
        audio_state = "Off"
    elif audio_state == "Off":
        audio_state = "On"

    menu.entryconfigure(3, label=f"Audio: {audio_state}")


def play_video():
    """
        This function handles frame display, audio and QR creation
        input - None
        output - None
    """
    global changed_video_location_status

    while True:
        # Find and list in reverse order all videos from video folder which was set in settings file
        path = settings.get_settings("video_directory:")
        files = os.listdir(path)
        video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv'))]
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)

        # Select last video from list of videos and retrieve original playback information
        latest_video = video_files[0]
        frame_data = imageio.get_reader(path + "/" + latest_video)
        frame_rate = frame_data.get_meta_data()['fps']

        # Extract audio from video and set Thread for future playback
        video_clip = VideoFileClip(path + "/" + latest_video)
        audio_clip = video_clip.audio
        audio_thread = Thread(target=audio_clip.preview)

        # Set QR size based on window length and width
        qr_size = int(0.3 * root.winfo_width() * width_constant)

        # Create Right QR
        qr_frame_right = ImageTk.PhotoImage(PIL.Image.fromarray(
            np.array(generate_qr.qr(text=f"http://{settings.get_settings('server_ip:')}:{settings.get_settings('server_port:')}"))).resize(
            (qr_size, qr_size),
            resample=PIL.Image.LANCZOS))

        # Create Left QR
        qr_frame_left = ImageTk.PhotoImage(PIL.Image.fromarray(
            np.array(
                generate_qr.qr(ssid=settings.get_settings("wifi_ssid:"), password=settings.get_settings("wifi_password:")))).resize(
            (qr_size, qr_size), resample=PIL.Image.LANCZOS))

        # If video data can be used start video play
        if frame_data is not None:
            # Start audio playback if flag was set to "On"
            if audio_state == "On":
                audio_thread.daemon = True
                audio_thread.start()

            start_time = time.time()  # Timer used for frame rate consistency
            for frame_number, frame in enumerate(frame_data.iter_data()):
                # If Videos location was changed stop playback
                if changed_video_location_status:
                    changed_video_location_status = False
                    break

                # Calculate timers before next frame can be displayed
                frame_time = frame_number / frame_rate
                elapsed_time = time.time() - start_time
                remaining_time = frame_time - elapsed_time

                # Wait until next frame should be displayed
                if remaining_time > 0:
                    time.sleep(remaining_time)

                # Set video frame onto Tkinter middle widget
                frame_image = ImageTk.PhotoImage(PIL.Image.fromarray(frame).resize((int(root.winfo_width() * width_constant), root.winfo_height())))
                middle_container.config(image=frame_image)
                middle_container.image = frame_image

                # Set right QR image to right Tkinter widget
                right_container.config(image=qr_frame_right)
                right_container.image = qr_frame_right

                # Set left QR image to left Tkinter widget
                left_container.config(image=qr_frame_left)
                left_container.image = qr_frame_left


def start_server_thread():
    """
        Function creates and starts a Thread for the flask server
        input - None
        output - None
    """
    server_thread = Thread(target=flask_server.run)
    server_thread.daemon = 1
    server_thread.start()

    messagebox.showinfo(title="Confirmation Box", message="Server was started")


def start_apache_server():
    os.startfile("C:\Apache24\\bin\httpd.exe")


def stop_apache_server():
    for pid in (process.pid for process in psutil.process_iter() if process.name() == "httpd.exe"):
        os.kill(pid, signal.SIGTERM)


def save_input_to_settings_file(message, input_box, data):
    """
        Function saves input(settings) to text file located in AppData
        input - message; Type STR
              - input_box; Type Tkinter Widget
              - data; Type DICT
        output - None
    """
    settings.write_settings(data)
    input_box.destroy()
    messagebox.showinfo(title="Confirmation Box", message=message)

    server_port_label.config(text=settings.get_settings("server_port:"))
    server_ip_label.config(text=settings.get_settings("server_ip:"))
    wifi_name_label.config(text="Name:" + str(settings.get_settings("wifi_ssid:")))
    wifi_password_label.config(text="Password:" + str(settings.get_settings("wifi_password:")))


def set_local_ip():
    """
        Function saves user input and sends it to settings file
        input - None
        output - None
    """
    # Create Tkinter Widget for input box
    ip_input_box = tk.Toplevel(root)
    ip_input_box.title("Enter local IP")

    # Create labels for Tkinter Widget
    ip_label = tk.Label(ip_input_box, text="IP:")
    ip_ssid = tk.Entry(ip_input_box)
    save_button = tk.Button(ip_input_box, text="Save",
                            command=lambda: save_input_to_settings_file("IP saved", ip_input_box,
                                                                        {"server_ip:": ip_ssid.get()}))

    # Place Widgets automatically with pack function
    ip_label.pack()
    ip_ssid.pack()
    save_button.pack()


def set_port():
    """
        Function saves user input and sends it to settings file
        input - None
        output - None
    """
    # Create Tkinter Widget for input box
    port_input_box = tk.Toplevel(root)
    port_input_box.title("Enter port")

    # Create labels for Tkinter Widget
    port_label = tk.Label(port_input_box, text="Port:")
    port_ssid = tk.Entry(port_input_box)
    save_button = tk.Button(port_input_box, text="Save",
                            command=lambda: save_input_to_settings_file("Port saved", port_input_box,
                                                                        {"server_port:": port_ssid.get()}))

    # Place Widgets automatically with pack function
    port_label.pack()
    port_ssid.pack()
    save_button.pack()


def set_videos_location():
    """
        Function saves input(settings) to text file located in AppData
        input - None
        output - None
    """
    global play_video_thread, changed_video_location_status

    # Create a Tkinter dialog object and save response
    videos_directory = filedialog.askdirectory()

    # If a response exists save data to settings file
    if len(videos_directory) > 0:
        settings.write_settings({"video_directory:": videos_directory})

    # If play video Thread is not active create and start it
    # if not play_video_thread.is_alive():
    #     play_video_thread = Thread(target=play_video)
    #     play_video_thread.daemon = 1
    #     play_video_thread.start()

    video_directory_label.config(text=settings.get_settings("video_directory:"))

    # Change flag to indicate video location has changed
    changed_video_location_status = True


def destroy_application():
    for pid in (process.pid for process in psutil.process_iter() if process.name() == "httpd.exe"):
        os.kill(pid, signal.SIGTERM)

    root.destroy()


def set_wifi_credentials():
    """
        Function saves user input and sends it to settings file
        input - None
        output - None
    """
    # Create Tkinter Widget for input box
    wifi_input_box = tk.Toplevel(root)
    wifi_input_box.title("Wifi Credentials")

    # Create labels for Tkinter Widget
    ssid_label = tk.Label(wifi_input_box, text="Wifi name:")
    password_label = tk.Label(wifi_input_box, text="Password:")
    ssid = tk.Entry(wifi_input_box)
    password = tk.Entry(wifi_input_box)
    save_button = tk.Button(wifi_input_box, text="Save",
                            command=lambda: save_input_to_settings_file("Wifi credentials saved", wifi_input_box,
                                                                        {"wifi_ssid:": ssid.get(),
                                                                         "wifi_password:": password.get()}))

    # Place Widgets automatically with pack function
    ssid_label.pack()
    ssid.pack()
    password_label.pack()
    password.pack()
    save_button.pack()


def create_qr():
    def on_selection_normal_qr_checkbox():
        if normal_qr_checkbox_value.get():  # If the first checkbox is selected
            wifi_qr_checkbox_value.set(False)

            wifi_ssid_entry.delete(0, tk.END)
            wifi_password_entry.delete(0, tk.END)

            wifi_ssid_entry.config(state=tk.DISABLED)
            wifi_password_entry.config(state=tk.DISABLED)
            normal_text_entry.config(state=tk.NORMAL)
        else:
            normal_text_entry.config(state=tk.DISABLED)


    def on_selection_wifi_qr_checkbox():
        if wifi_qr_checkbox_value.get():  # If the second checkbox is selected
            normal_qr_checkbox_value.set(False)

            normal_text_entry.delete(0, tk.END)

            normal_text_entry.config(state=tk.DISABLED)
            wifi_ssid_entry.config(state=tk.NORMAL)
            wifi_password_entry.config(state=tk.NORMAL)
        else:
            wifi_ssid_entry.config(state=tk.DISABLED)
            wifi_password_entry.config(state=tk.DISABLED)


    def add_background():
        nonlocal background_image_path

        if add_background_checkbox_value.get():  # If checkbox is selected
            background_image_path = filedialog.askopenfilename(
                title="Select an image",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg"), ("JPG files", "*.jpg"), ("All files", "*.*")]
            )
            add_background_checkbox.config(text=background_image_path)

            enable_transparency_checkbox_value.set(False)


    def enable_transparency():
        if enable_transparency_checkbox_value.get():
            enable_transparency_checkbox_value.set(True)
            add_background_checkbox_value.set(False)


    def create_qr_request():
        if normal_qr_checkbox_value.get():
            generate_qr.qr(background_image_path, enable_transparency_checkbox_value.get(),
                        text = normal_text_entry.get(), )
        elif wifi_qr_checkbox_value.get():
            generate_qr.qr(background_image_path, enable_transparency_checkbox_value.get(),
                        wifi_ssid = wifi_ssid_entry.get(), wifi_password = wifi_password_entry.get())

        qr_window.destroy()

    # Create a new window
    qr_window = tk.Toplevel(root)
    qr_window.title("QR Creation")
    qr_window.geometry("320x200")
    qr_window.resizable(False, False)

    # Create a variable to store the state of the checkbox
    normal_qr_checkbox_value = tk.BooleanVar(value=True)
    wifi_qr_checkbox_value = tk.BooleanVar(value=False)
    add_background_checkbox_value = tk.BooleanVar(value=False)
    enable_transparency_checkbox_value = tk.BooleanVar(value=False)

    background_image_path = None

    # Create and pack the first entry (enabled by default)
    normal_text_entry = ttk.Entry(qr_window)
    normal_text_entry.place(x=25, y=40)

    # Create and pack the second and third entries (disabled by default)
    wifi_ssid_entry = ttk.Entry(qr_window, state=tk.DISABLED)
    wifi_ssid_entry.place(x=170, y=40)

    wifi_password_entry = ttk.Entry(qr_window, state=tk.DISABLED)
    wifi_password_entry.place(x=170, y=70)

    # Create and pack the checkboxes
    normal_qr_checkbox = ttk.Checkbutton(qr_window, text="Normal QR", variable=normal_qr_checkbox_value, command=on_selection_normal_qr_checkbox)
    normal_qr_checkbox.place(x=50, y=10)

    wifi_qr_checkbox = ttk.Checkbutton(qr_window, text="Wifi QR", variable=wifi_qr_checkbox_value, command=on_selection_wifi_qr_checkbox)
    wifi_qr_checkbox.place(x=195, y=10)

    add_background_checkbox = ttk.Checkbutton(qr_window, text="Add Background", variable=add_background_checkbox_value, command=add_background)
    add_background_checkbox.place(x=25, y=100)

    enable_transparency_checkbox = ttk.Checkbutton(qr_window, text="Enable Transparency", variable=enable_transparency_checkbox_value, command=enable_transparency)
    enable_transparency_checkbox.place(x=25, y=130)

    # Create a button to save the text from the entries and create the QR
    save_button = ttk.Button(qr_window, text="Create QR", command=create_qr_request)
    save_button.place(x=185, y=120)


# Create settings file if it's first time application was started on this machine
settings.set_default_settings()

# Main window Characteristics
root = tk.Tk()
root.title("360 Gallery")
root.geometry("475x375")

window_width = root.winfo_width()
window_height = root.winfo_height()

# Create a style for main widget
style = ttk.Style(root)
# Set the theme with the theme_use method
style.theme_use('vista')


# Menu Objects
# menubar = Menu(root)
# menu = Menu(menubar, tearoff=0)
# server_menu = Menu(menu, tearoff=0)

# Create droplists for submenus
# menubar.add_cascade(label="Menu", menu=menu)
# menu.add_cascade(label="Server", menu=server_menu)

# Create commands for menus buttons
# server_menu.add_command(label="Start Server", command=start_server_thread)
# server_menu.add_command(label="Save IP", command=set_local_ip)
# server_menu.add_command(label="Save Port", command=set_port)
# menu.add_command(label="Video Directory", command=set_videos_location)
# menu.add_command(label="Wifi", command=set_wifi_credentials)
# menu.add_command(label=f"Audio: {audio_state}", command=change_audio_state)

# Place main menu into Tkinter main window
# root.config(menu=menubar)


# Create background image, set it to a Tkinter label and tie label to main window
image = PIL.Image.open("templates/background.png").resize((1920, 1080))
image_array = PIL.Image.fromarray(np.array(image))
background_image = ImageTk.PhotoImage(image_array)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Create containers for QRs and video and place them onto Tkinter window
# left_container = ttk.Label(root)
# left_container.pack(side="left", expand=True,  padx=10)
# middle_container = ttk.Label(root)
# middle_container.pack(side="left", expand=True, padx=10)
# right_container = ttk.Label(root)
# right_container.pack(side="left", expand=True,  padx=10)

# Create QR Images and tie them to their container
# left_qr = ImageTk.PhotoImage(generate_qr.qr(ssid=settings.get_settings("wifi_ssid:"), password=settings.get_settings("wifi_password:")))
# left_container.config(image=left_qr)
# right_qr = ImageTk.PhotoImage(generate_qr.qr(text=f"http://{settings.get_settings('server_ip:')}:{settings.get_settings('server_port:')}"))
# right_container.config(image=right_qr)


# Threads
# play_video_thread = Thread(target=play_video)
# play_video_thread.daemon = 1
# play_video_thread.start()

# fullscreen_thread = Thread(target=set_fullscreen_variable)
# fullscreen_thread.daemon = 1
# fullscreen_thread.start()

# make_window_fullscreen()


# Create commands for menus buttons
# server_menu.add_command(label="Start Server", command=start_server_thread)
# server_menu.add_command(label="Save IP", command=set_local_ip)
# server_menu.add_command(label="Save Port", command=set_port)
# menu.add_command(label="Video Directory", command=set_videos_location)
# menu.add_command(label="Wifi", command=set_wifi_credentials)
# menu.add_command(label=f"Audio: {audio_state}", command=change_audio_state)


# Create buttons to replace menu entries
start_server_button = tk.Button(root, text="Start Server", command=start_apache_server)
start_server_button.place(x=25, y=30)

stop_server_button = tk.Button(root, text="Stop Server", command=stop_apache_server)
stop_server_button.place(x=100, y=30)

save_ip_button = tk.Button(root, text="Save IP", command=set_local_ip)
save_ip_button.place(x=25, y=60)

save_port_button = tk.Button(root, text="Save Port", command=set_port)
save_port_button.place(x=25, y=90)

save_wifi_credentials_button = tk.Button(root, text="Change Wifi Credentials", command=set_wifi_credentials)
save_wifi_credentials_button.place(x=25, y=150)

save_video_location_button = tk.Button(root, text="Change Video Directory", command=set_videos_location)
save_video_location_button.place(x=25, y=190)

create_qr_button = tk.Button(root, text="Create QR", command=create_qr)
create_qr_button.place(x=25, y=250)

quit_button = tk.Button(root, text="Quit", command=destroy_application)
quit_button.place(x=430, y=325)


# Create labels for each of the button entry
server_ip_label = ttk.Label(root, text=settings.get_settings("server_ip:"))
server_ip_label.place(x=180, y=65)

server_port_label = ttk.Label(root, text=settings.get_settings("server_port:"))
server_port_label.place(x=180, y=95)

wifi_name_label = ttk.Label(root, text="Name:" + str(settings.get_settings("wifi_ssid:")))
wifi_name_label.place(x=180, y=145)

wifi_password_label = ttk.Label(root, text="Password:" + str(settings.get_settings("wifi_password:")))
wifi_password_label.place(x=180, y=165)

video_directory_label = ttk.Label(root, text=settings.get_settings("video_directory:"))
video_directory_label.place(x=180, y=195)

root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", destroy_application)
root.mainloop()
