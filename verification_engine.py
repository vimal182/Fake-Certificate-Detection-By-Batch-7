import os
import cv2
import torch
import numpy as np
from torchvision import transforms



# DEVICE


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "mobilenet_forgery.pt")

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)



# LOAD MODEL 


def load_model():
    try:
        model = torch.jit.load(MODEL_PATH, map_location=DEVICE)
        model.eval()
        return model
    except Exception as e:
        print("Model loading error:", e)
        raise


model = load_model()



# IMAGE PREPROCESSING


transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])



# GRADCAM IMPLEMENTATION


def generate_gradcam(input_tensor):

    input_tensor.requires_grad = True

    output = model(input_tensor)
    class_idx = torch.argmax(output)

    model.zero_grad()
    output[0, class_idx].backward()

    gradients = input_tensor.grad.data
    pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])

    heatmap = torch.mean(input_tensor[0], dim=0).cpu().detach().numpy()

    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap) + 1e-8

    return heatmap



# BOUNDING BOX FROM HEATMAP


def get_bounding_box(heatmap):

    heatmap_uint8 = np.uint8(255 * heatmap)
    _, thresh = cv2.threshold(heatmap_uint8, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        return (x, y, w, h)

    return None



# MAIN VERIFICATION FUNCTION


def verify_certificate(image_path, threshold=0.85, alpha=0.5):

    image = cv2.imread(image_path)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    input_tensor = transform(rgb_image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)
        confidence = float(torch.max(probs)) * 100
        predicted_class = torch.argmax(probs).item()

    
    if predicted_class == 0:
        ai_status = "GENUINE"
    else:
        ai_status = "FORGED"

    risk_level = "LOW"
    if confidence > (threshold * 100):
        risk_level = "HIGH"

    
    heatmap = generate_gradcam(input_tensor)

    heatmap_resized = cv2.resize(
        heatmap,
        (image.shape[1], image.shape[0])
    )

    heatmap_colored = cv2.applyColorMap(
        np.uint8(255 * heatmap_resized),
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(
        image,
        1 - alpha,
        heatmap_colored,
        alpha,
        0
    )

    heatmap_path = os.path.join(
        OUTPUT_DIR,
        f"heatmap_{os.path.basename(image_path)}"
    )

    cv2.imwrite(heatmap_path, overlay)

    bbox = get_bounding_box(heatmap_resized)

    return {
        "ai_status": ai_status,
        "confidence": round(confidence, 2),
        "risk_level": risk_level,
        "heatmap_path": heatmap_path,
        "bbox": bbox
    }