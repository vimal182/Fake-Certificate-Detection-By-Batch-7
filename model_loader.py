# ai/model_loader.py

import os
import platform
import psutil
import onnxruntime as ort


# GLOBAL STATE


DEVICE_TYPE = "CPU"
DEVICE_NAME = platform.processor()
TOTAL_RAM = round(psutil.virtual_memory().total / (1024 ** 3), 2)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "mobilenet_forgery.onnx")

onnx_session = None



# HARDWARE INFO 


def detect_hardware():
    global DEVICE_TYPE, DEVICE_NAME
    DEVICE_TYPE = "CPU"
    DEVICE_NAME = platform.processor()

    return DEVICE_TYPE, DEVICE_NAME, TOTAL_RAM


def get_device_type():
    return DEVICE_TYPE


def get_device_name():
    return DEVICE_NAME


def get_total_ram():
    return TOTAL_RAM



# MODEL LOADING


def load_model():
    global onnx_session

    print("Loading ONNX MobileNet Forgery Model...")

    onnx_session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    print("ONNX Model Loaded Successfully.")