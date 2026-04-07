import cv2
import numpy as np

def detect_seal(image):

    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    circles=cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=40,
        maxRadius=200
    )

    boxes=[]

    if circles is not None:

        circles=np.uint16(np.around(circles))

        for x,y,r in circles[0,:]:

            boxes.append((x-r,y-r,2*r,2*r))

    return boxes