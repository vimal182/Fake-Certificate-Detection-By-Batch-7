import cv2
import pytesseract
import numpy as np

# Windows Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def detect_text_tampering(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    output = image.copy()

    for i, text in enumerate(data["text"]):

        if text.strip() == "":
            continue

        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        region = gray[y:y+h, x:x+w]

        
        lap = cv2.Laplacian(region, cv2.CV_64F)
        score = np.var(lap)

        
        if score > 70:
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 255), 2)

    return output