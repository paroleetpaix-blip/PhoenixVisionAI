"""
========================================================
PHOENIX VISION AI

AI Server

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import tempfile
import shutil

app = FastAPI(
    title="Phoenix Vision AI Server"
)

# Chargement du modèle YOLO
from config import MODEL_NAME

model = YOLO(MODEL_NAME)


@app.get("/health")
def health():

    return {
        "status": "online",
        "model": "YOLOv8n"
    }


@app.post("/predict")
async def predict(image: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False) as tmp:

        shutil.copyfileobj(image.file, tmp)

        image_path = tmp.name

    results = model(image_path)

    detections = []

    for result in results:

        for box in result.boxes:

            detections.append({

                "label": model.names[int(box.cls)],

                "confidence": float(box.conf),

                "bbox": box.xyxy[0].tolist()

            })

    return {

        "detections": detections

    }