# qr/qr_generator.py

import qrcode
import json
import os


def generate_qr(data, filename):

    os.makedirs("qr_codes", exist_ok=True)

    qr_data = json.dumps(data, separators=(",", ":"))

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    path = f"qr_codes/{filename}.png"
    img.save(path)

    return path