# mobilenet_utils.py

import os
import torch
from torchvision import transforms
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "mobilenet_forgery.pt")

DEVICE = torch.device("cpu")

#  Load model
model = torch.jit.load(MODEL_PATH, map_location=DEVICE)
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def predict(image_path):
    image = Image.open(image_path).convert("RGB")
    img_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(img_tensor)

        #  Softmax output
        probabilities = torch.softmax(output, dim=1)
        confidence, predicted_class = torch.max(probabilities, dim=1)

        confidence = confidence.item()
        predicted_class = predicted_class.item()

    label = "FAKE" if predicted_class == 1 else "ORIGINAL"

    return {"label": label, "confidence": confidence}


def get_input_tensor(image_path):
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0).to(DEVICE)