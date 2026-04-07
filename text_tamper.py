import pytesseract
import cv2

def detect_text_tampering(image):

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(gray,output_type=pytesseract.Output.DICT)

    boxes = []

    for i,text in enumerate(data["text"]):

        if len(text.strip())>0:

            x=data["left"][i]
            y=data["top"][i]
            w=data["width"][i]
            h=data["height"][i]

            boxes.append((x,y,w,h))

    return boxes