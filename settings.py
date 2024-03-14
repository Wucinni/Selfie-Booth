#############################################
#                                           #
# This script manages settings file located #
#          in AppData Directory             #
#                                           #
#  It handles input and output to the user  #
#         and the other modules             #
#                                           #
#############################################


import os
import subprocess


def get_wlan_ip():
    """
        Function retrieves IPv4 Address for the current Wi-Fi adapter connection
        input - None
        output - IPv4 Address; Type STR
    """
    # Send command to retrieve all network adapters
    network_adapters = subprocess.run('ipconfig', stdout=subprocess.PIPE, text=True).stdout.lower()

    found_wifi_adapter = False
    for adapter in network_adapters.split('\n'):
        if 'wireless' and 'wifi' in adapter:
            found_wifi_adapter = True
        if found_wifi_adapter:
            if 'ipv4' in adapter:
                return adapter.split(':')[1].strip()


def get_user():
    """
        Function retrieves OS Username
        input - None
        output - username; Type STR
    """
    username = os.getenv("USERNAME")
    return username


def get_path_to_settings_file():
    """
        Function retrieves path to this application settings file
        input - None
        output - path; Type STR
    """
    path = "C:\\Users\\{}\\AppData\\Local\\360Gallery".format(get_user())
    return path


def set_default_settings():
    """
        Function writes default settings to settings file in AppData if it doesn't exist
        input - None
        output - None
    """
    path = get_path_to_settings_file()

    # Create directory if it doesn't exist
    if not os.path.exists(path):
        os.mkdir(path)

    # Write settings data to file
    try:
        file = open(path + "\\settings.txt", "x")
        file.write(f"video_directory:C:\\Users\\{get_user()}\\Desktop\n")
        file.write("wifi_ssid:wifi\n")
        file.write("wifi_password:password\n")
        file.write(f"server_ip:{str(get_wlan_ip())}\n")
        file.write("server_port:5000\n")
        file.close()
    except:
        print("Settings File Exists.")


def write_settings(data):
    """
        Function writes data to settings file located in AppData
        input - data; Type DICT -> {tag: value}
        output - None
    """
    # Get old text in a variable
    file = open(get_path_to_settings_file() + "\\settings.txt", "r")
    lines = file.readlines()

    # Iterate through data and modify where tag(setting_to_be_written) is found
    for setting_to_be_written in data:
        for position, text in enumerate(lines):
            if setting_to_be_written in text:
                lines[position] = f"{setting_to_be_written}{data[setting_to_be_written]}\n"

    # Rewrite to file with new data
    file = open(get_path_to_settings_file() + "\\settings.txt", "w")
    file.writelines(lines)
    file.close()


def get_settings(tag):
    """
        Function retrieves data form settings file located in AppData where tag is found
        input - tag; Type STR
        output - setting; Type STR
    """
    # Open file and read data
    file = open(get_path_to_settings_file() + "\\settings.txt", "r")
    lines = file.readlines()

    # If tag is found in current line return text
    for position, text in enumerate(lines):
        if tag in text:
            return text[len(tag):-1]
