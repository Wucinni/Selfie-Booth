from PIL import Image, ImageDraw, ImageFont
import wifi_qrcode_generator.generator
import qrcode


def generate_qr_code2(text=None, tag="VIDEO"):
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr_code.add_data(text)
    qr_code.make(fit=True)
    # qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
    qr_code_image = qr_code.make_image(fill_color="black", back_color="white")
    # 255 213 129

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


def generate_qr_code3(text=None, background_image_path="C:\\Users\Dennis\PycharmProjects\Selfie-Booth\\templates\\background_qr_right.png"):
    # Generate QR code with white background
    qr_code = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_code.add_data(text)
    qr_code.make(fit=True)
    qr_code_image = qr_code.make_image(fill_color="white", back_color="black")  # Black QR code on white background

    # Load background image
    background = Image.open(background_image_path)

    # Resize background image to fit QR code
    qr_code_size = qr_code_image.size
    background = background.resize(qr_code_size)

    # Convert QR code image to RGBA mode to ensure transparency
    qr_code_image_rgba = qr_code_image.convert("RGBA")

    # Create a mask to identify white pixels in the QR code
    mask = qr_code_image.convert("L")
    mask = Image.eval(mask, lambda px: 255 if px == 255 else 0)

    # Paste QR code onto background image with transparency
    background.paste(qr_code_image_rgba, (0, 0), mask)

    return background

def generate_qr_code(text = None, tag = None):
    # generate_qr_code2().show()
    image1 = generate_qr_code2(text).convert("RGB")
    image2 = generate_qr_code3(text).convert("RGB")

    # Get pixel data from both images
    pixels1 = image1.load()
    pixels2 = image2.load()

    # Ensure both images have the same size
    if image1.size != image2.size:
        image1 = image1.resize(image2.size)

    # Iterate through each pixel of the first image
    for x in range(image1.width):
        for y in range(image1.height):
            # Get the RGB values of the pixel
            r, g, b = pixels1[x, y]
            # If the pixel in the first image is black, paste it onto the second image
            if r == g == b == 0:
                pixels2[x, y] = (0, 0, 0)  # Set the corresponding pixel in the second image to black

    # image2.show()
    return image2

    # Now you can continue using image1 and image2 as modified variables in your code