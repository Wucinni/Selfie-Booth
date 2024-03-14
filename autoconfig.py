import subprocess
import sys

module_list = ["flask", "imageio[ffmpeg]", "keyboard", "moviepy", "numpy", "pillow", "qrcode", "thread6", "tk", "wifi_qrcode_generator"]

for module in module_list:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', module])
    except:
        pass
