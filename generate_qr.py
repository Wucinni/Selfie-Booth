#############################################
#                                           #
#       This script calculates QRs and      #
#           create their images             #
#                                           #
#############################################


import os
from PIL import Image
import qrcode
import wifi_qrcode_generator.generator


filename = os.path.basename(__file__)
path = os.path.abspath(__file__)


def set_qr_background(qr_code_image, modified_qr_code_image, background):
    """
        This function combines a default QR and a modified QR to create one with background
        input - qr_code_image: Type Pillow Image
              - modified_qr_code_image: Type Pillow Image
              - path to background: Type STR
        output - QR; Type Pillow Image
    """

    # Load background image and resize to fit QR
    background = Image.open(background)
    qr_code_size = modified_qr_code_image.size
    resized_background = background.resize(qr_code_size)

    # Convert QR code image to RGBA mode to ensure transparency
    qr_code_image_rgba = modified_qr_code_image.convert("RGBA")

    # Create mask to find white pixels in QR
    mask = modified_qr_code_image.convert("L")
    mask = Image.eval(mask, lambda px: 255 if px == 255 else 0)

    # Paste QR code onto background image with transparency
    resized_background.paste(qr_code_image_rgba, (0, 0), mask)

    qr_code_image = qr_code_image.convert("RGB")
    modified_qr_code_image = resized_background.convert("RGB")

    # Get pixel data from both images
    pixels_qr = qr_code_image.load()
    pixels_modified_qr = modified_qr_code_image.load()

    # Ensure both images have the same size
    if qr_code_image.size != modified_qr_code_image.size:
        qr_code_image = qr_code_image.resize(modified_qr_code_image.size)

    # Iterate through each pixel of the first image
    for pixel_x_position in range(qr_code_image.width):
        for pixel_y_position in range(qr_code_image.height):
            # Get the RGB values of the pixel
            r, g, b = pixels_qr[pixel_x_position, pixel_y_position]
            # If the pixel in the first image is black, paste it onto the second image
            if r == g == b == 0:
                pixels_modified_qr[pixel_x_position, pixel_y_position] = (
                0, 0, 0)  # Set the corresponding pixel in the second image to black

    return modified_qr_code_image


def qr(ssid=None, password=None, text=None):
    """
        Function creates a QR Image based on text
        input - Wi-Fi ssid: Type STR
              - Wi-fi password: Type STR
              - plain text: Type STR
        output - QR; Type Pillow Image
    """
    # If text exists create a standard QR and set background to appropriate image
    if text:
        background = path[:len(path) - len(filename)] + "templates\\background_qr_right.png"
        qr_code = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr_code.add_data(text)
        qr_code.make(fit=True)

    # If ssid exists create a Wi-Fi QR and set background to appropriate image
    elif ssid:
        background = path[:len(path) - len(filename)] + "templates\\background_qr_left.png"
        if password:
            qr_code = wifi_qrcode_generator.generator.wifi_qrcode(
                ssid=ssid, hidden=False, authentication_type='WPA', password=password
            )
        else:
            qr_code = wifi_qrcode_generator.generator.wifi_qrcode(
                ssid=ssid, hidden=False, authentication_type='nopass', password=None
            )

    return set_qr_background(qr_code.make_image(fill_color="black", back_color="white"), qr_code.make_image(fill_color="white", back_color="black"), background)
