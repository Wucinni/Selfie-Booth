from PIL import Image, ImageDraw, ImageFont
import wifi_qrcode_generator.generator
import qrcode
import os


filename = os.path.basename(__file__)
path = os.path.abspath(__file__)


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


def generate_qr_code(text=None):
    # Create QR Object
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr_code.add_data(text)
    qr_code.make(fit=True)

    # Create QR Images from QR Objects
    qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
    modified_qr_code_image = qr_code.make_image(fill_color="white", back_color="black")

    # Load background image and resize to fit QR
    background = Image.open(path[:len(path) - len(filename)] + "templates\\background_qr_right.png")
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
                pixels_modified_qr[pixel_x_position, pixel_y_position] = (0, 0, 0)  # Set the corresponding pixel in the second image to black

    # modified_qr_code_image.show()
    return modified_qr_code_image
