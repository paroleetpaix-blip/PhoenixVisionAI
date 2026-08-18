"""
========================================================
PHOENIX VISION AI

AI Server

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

import os
import shutil
import tempfile

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile
)

from ultralytics import YOLO

from config import (
    MODEL_NAME,
    CONFIDENCE
)


app = FastAPI(

    title="Phoenix Vision AI Server",

    version="0.6.0"

)


# ========================================================
# MODEL
# ========================================================

print(
    "Chargement du modèle Phoenix AI :",
    MODEL_NAME
)


model = YOLO(
    MODEL_NAME
)


print(
    "✓ Modèle YOLO prêt."
)


# ========================================================
# HEALTH
# ========================================================

@app.get(
    "/health"
)
def health():

    return {

        "status":
            "online",

        "service":
            "Phoenix Vision AI Server",

        "backend":
            "Ultralytics YOLO",

        "model":
            MODEL_NAME

    }


# ========================================================
# PREDICT
# ========================================================

@app.post(
    "/predict"
)
async def predict(

    image: UploadFile = File(...)

):

    if image is None:

        raise HTTPException(

            status_code=400,

            detail="Image absente."

        )


    suffix = os.path.splitext(
        image.filename
        or
        "frame.jpg"
    )[1]


    if not suffix:

        suffix = ".jpg"


    image_path = None


    try:

        with tempfile.NamedTemporaryFile(

            suffix=suffix,

            delete=False

        ) as temporary_file:

            shutil.copyfileobj(

                image.file,

                temporary_file

            )


            image_path = (
                temporary_file.name
            )


        results = model.predict(

            source=image_path,

            conf=CONFIDENCE,

            verbose=False

        )


        detections = []


        for result in results:

            for box in result.boxes:

                class_id = int(
                    box.cls.item()
                )


                confidence = float(
                    box.conf.item()
                )


                bbox = (

                    box.xyxy[0]
                    .cpu()
                    .tolist()

                )


                detections.append({

                    "label":
                        model.names[
                            class_id
                        ],

                    "confidence":
                        confidence,

                    "bbox":
                        bbox

                })


        return {

            "success":
                True,

            "model":
                MODEL_NAME,

            "detections":
                detections

        }


    finally:

        if (
            image_path
            and
            os.path.exists(
                image_path
            )
        ):

            try:

                os.remove(
                    image_path
                )

            except OSError:

                pass