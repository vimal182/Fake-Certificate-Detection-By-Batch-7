import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance

from ai import model_loader
from ai.gradcam_utils import overlay_heatmap
from ai.ocr_text_detector import detect_text_tampering



# ELA


def perform_ela(image_path):
    original = Image.open(image_path).convert("RGB")
    temp_path = "temp_ela.jpg"
    original.save(temp_path, "JPEG", quality=90)
    compressed = Image.open(temp_path)

    ela_image = ImageChops.difference(original, compressed)
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    scale = 255.0 / max_diff if max_diff != 0 else 1
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    return cv2.cvtColor(np.array(ela_image), cv2.COLOR_RGB2BGR)



# NOISE MAP


def noise_analysis(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    noise = cv2.absdiff(gray, blur)
    return cv2.applyColorMap(noise, cv2.COLORMAP_JET)



# SEAL + SIGNATURE DETECTION


def detect_seal_signature(image_path):

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    output = img.copy()

    seal_status = "SUSPICIOUS"
    signature_status = "SUSPICIOUS"

    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=30,
        maxRadius=150
    )

    if circles is not None:
        seal_status = "AUTHENTIC"
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :1]:
            x, y, r = circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 3)

    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    large_strokes = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]

    if len(large_strokes) > 5:
        signature_status = "AUTHENTIC"
        for cnt in large_strokes[:3]:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return seal_status, signature_status, output



# GRADCAM GENERATION 


def generate_gradcam(image_path):

    image = cv2.imread(image_path)
    image_resized = cv2.resize(image, (224, 224))

    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(image_resized, 0.6, heatmap, 0.4, 0)

    return overlay



# MAIN ANALYSIS


def analyze_certificate(image_path):

    
    if model_loader.onnx_session is None:
        model_loader.load_model()

    device_type = model_loader.get_device_type()

    original = cv2.imread(image_path)

    # OCR text tamper detection
    text_bbox = detect_text_tampering(original)

    rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

    #  ONNX MODEL 
    session = model_loader.onnx_session

    img = cv2.resize(rgb, (224, 224)).astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img})

    output = outputs[0]

    if output.shape[-1] == 1:
        prob = float(output[0][0])
        prob = max(0.0, min(prob, 1.0))
        pred = 1 if prob > 0.5 else 0
        confidence = prob
    else:
        exp_scores = np.exp(output)
        probs = exp_scores / np.sum(exp_scores)
        pred = int(np.argmax(probs))
        confidence = float(np.max(probs))

    label = "FORGED" if pred == 0 else "GENUINE"

    seal_status, signature_status, bbox_img = detect_seal_signature(image_path)

    gradcam_img = generate_gradcam(image_path)

    return {
        "mode": device_type,
        "label": label,
        "confidence": round(confidence * 100, 2),
        "gradcam": gradcam_img,
        "ela": perform_ela(image_path),
        "noise": noise_analysis(original),
        "seal_status": seal_status,
        "signature_status": signature_status,
        "bbox_image": text_bbox
    }