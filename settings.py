import os


def get_wlan_ip():
    import subprocess
    result = subprocess.run('ipconfig', stdout=subprocess.PIPE, text=True).stdout.lower()
    scan = 0
    for i in result.split('\n'):
        if 'wireless' in i: scan = 1
        if scan:
            if 'ipv4' in i: return i.split(':')[1].strip()


def get_user():
    username = os.getenv("USERNAME")
    return username


def get_path():
    path = "C:\\Users\\{}\\AppData\\Local\\360Gallery".format(get_user())
    return path


def set_default_settings():
    path = get_path()

    if not os.path.exists(path):
        os.mkdir(path)
        print("Made directory")

    try:
        file = open(path + "\\settings.txt", "x")
        file.write(f"video_directory:C:\\Users\\{get_user()}\\Desktop\n")
        file.write("wifi_ssid:\n")
        file.write("wifi_password:\n")
        file.write(f"server_ip:{str(get_wlan_ip())}\n")
        file.write("server_port:5000\n")
        file.close()
    except:
        print("Settings File Exists.")


def write_settings(settings_text, tag):
    file = open(get_path() + "\\settings.txt", "r")
    lines = file.readlines()

    for position, text in enumerate(lines):
        if tag in text:
            lines[position] = f"{tag}{settings_text}\n"
            break

    file = open(get_path() + "\\settings.txt", "w")
    file.writelines(lines)
    file.close()


def get_settings(tag):
    file = open(get_path() + "\\settings.txt", "r")
    lines = file.readlines()

    for position, text in enumerate(lines):
        if tag in text:
            return text[len(tag):-1]


def set_videos_folder(path):
    tag = "video_directory:"
    write_settings(path, tag)


def set_wifi_ssid(name):
    tag = "wifi_ssid:"
    write_settings(name, tag)


def set_wifi_password(password):
    tag = "wifi_password:"
    write_settings(password, tag)


def set_server_ip(ip):
    tag = "server_ip:"
    write_settings(ip, tag)


def set_server_port(port):
    tag = "server_port:"
    write_settings(str(port), tag)


def get_videos_folder():
    tag = "video_directory:"
    return get_settings(tag)


def get_wifi_ssid():
    tag = "wifi_ssid:"
    return get_settings(tag)


def get_wifi_password():
    tag = "wifi_password:"
    return get_settings(tag)


def get_server_ip():
    tag = "server_ip:"
    return get_settings(tag)


def get_server_port():
    tag = "server_port:"
    return get_settings(tag)
