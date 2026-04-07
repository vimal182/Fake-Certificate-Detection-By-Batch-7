import cv2

def detect_signature(image):

    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    _,th=cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV)

    contours,_=cv2.findContours(
        th,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    sig_boxes=[]

    for c in contours:

        area=cv2.contourArea(c)

        if 200<area<5000:

            x,y,w,h=cv2.boundingRect(c)

            if w>40 and h<80:
                sig_boxes.append((x,y,w,h))

    return sig_boxes