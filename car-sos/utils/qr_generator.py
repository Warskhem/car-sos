import os
import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
import base64
import secrets
import string

QR_CHARS = string.ascii_uppercase + string.digits

def generate_unique_code(length=8):
    return ''.join(secrets.choice(QR_CHARS) for _ in range(length))

def generate_qr_image(data, box_size=10, border=4):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def qr_to_base64(data, box_size=10, border=4):
    img = generate_qr_image(data, box_size, border)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

def generate_multiple_codes(count=100):
    codes = []
    for _ in range(count):
        codes.append(generate_unique_code())
    return codes
