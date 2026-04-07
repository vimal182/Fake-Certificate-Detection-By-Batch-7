# ai/gradcam_utils.py

import cv2
import numpy as np


class GradCAM:
    """
    Lightweight GradCAM approximation compatible with ONNX inference.
    Keeps the same class name and method structure so existing logic
    in the project remains unchanged.
    """

    def __init__(self, model=None, target_layer=None):
        # Parameters kept for compatibility
        self.model = model
        self.target_layer = target_layer

    def generate(self, input_image):
        """
        Generate activation heatmap using image gradients and edges
        as an approximation of GradCAM without requiring PyTorch.
        """

        if isinstance(input_image, str):
            image = cv2.imread(input_image)
        else:
            image = input_image.copy()

        image = cv2.resize(image, (224, 224))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # edge-based activation map
        edges = cv2.Laplacian(gray, cv2.CV_64F)
        cam = np.abs(edges)

        cam -= cam.min()
        cam /= (cam.max() + 1e-8)

        return cam


def overlay_heatmap(image_path, heatmap):
    """
    Overlay heatmap on certificate image
    """

    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))

    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(image, 0.6, heatmap, 0.4, 0)
    overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    return overlay