import sys
import subprocess

module_list = ["tk", "imageio[ffmpeg]", "pillow", "thread6", "keyboard", "numpy", "moviepy", "flask", "qrcode", "wifi_qrcode_generator"]

for module in module_list:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
    except:
        pass
