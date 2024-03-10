import wifi_qrcode_generator.generator
import qrcode


def generate_qr_code(text=None):
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr_code.add_data(text)
    qr_code.make(fit=True)
    qr_code_image = qr_code.make_image(fill_color="black", back_color="white")

    return qr_code_image


def generate_qr_wifi(ssid=None, password=None):
    if password is not None:
        qr_code = wifi_qrcode_generator.generator.wifi_qrcode(
            ssid=ssid, hidden=False, authentication_type='WPA', password=password
        )
    else:
        qr_code = wifi_qrcode_generator.generator.wifi_qrcode(
            ssid=ssid, hidden=False, authentication_type='nopass', password=None
        )

    return qr_code.make_image()
