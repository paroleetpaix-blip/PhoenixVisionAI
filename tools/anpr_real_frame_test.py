"""
========================================================
PHOENIX VISION AI

ANPR Real Frame Test

Phoenix Security Technologies
========================================================
"""

from pathlib import Path

import sys


# ========================================================
# PROJECT ROOT
# ========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


project_root_string = str(
    PROJECT_ROOT
)


if (
    project_root_string
    not in sys.path
):

    sys.path.insert(
        0,
        project_root_string
    )


# ========================================================
# IMPORTS
# ========================================================

import cv2

from core.detector import Detector

from detection.plate_reader import PlateReader


# ========================================================
# PATHS
# ========================================================

INPUT_IMAGE = (
    PROJECT_ROOT
    /
    "frames"
    /
    "frame_000013.jpg"
)


OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    /
    "outputs"
)


OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_IMAGE = (
    OUTPUT_DIRECTORY
    /
    "anpr_real_frame_test.jpg"
)


# ========================================================
# START
# ========================================================

print()

print(
    "=============================================="
)

print(
    "PHOENIX ANPR — REAL ROAD FRAME TEST"
)

print(
    "=============================================="
)

print()


# ========================================================
# IMAGE
# ========================================================

frame = cv2.imread(
    str(
        INPUT_IMAGE
    )
)


if frame is None:

    raise SystemExit(

        "ERREUR : impossible de lire "
        f"{INPUT_IMAGE}"

    )


height, width = (
    frame.shape[:2]
)


print(
    "Image :",
    INPUT_IMAGE
)


print(
    "Résolution :",
    f"{width}x{height}"
)


# ========================================================
# DETECTOR
# ========================================================

print()

print(
    "Chargement du détecteur..."
)


detector = Detector(
    backend="COLAB"
)


# ========================================================
# LOAD YOLO MODEL
# ========================================================

detector.load()


print(
    "Modèle IA chargé."
)


print(
    "Détection des véhicules..."
)


detections = detector.detect(
    frame
)


if detections is None:

    detections = []


print(
    "Détections :",
    len(detections)
)


# ========================================================
# PLATE READER
# ========================================================

plate_reader = PlateReader(

    # Pour ce test réel,
    # on conserve un seuil relativement permissif
    # afin d'observer ce que l'OCR arrive à lire.

    min_confidence=25.0,

    min_length=4,

    max_length=12

)


print(
    "Tesseract :",
    plate_reader.is_available()
)


print()


# ========================================================
# VEHICLE LABELS
# ========================================================

VEHICLE_LABELS = {

    "car",
    "truck",
    "bus",
    "motorcycle",
    "motorbike",
    "vehicle"

}


vehicle_count = 0

plate_count = 0


# ========================================================
# PROCESS
# ========================================================

for index, detection in enumerate(
    detections,
    start=1
):


    label = str(
        getattr(
            detection,
            "label",
            ""
        )
    ).lower()


    confidence = getattr(
        detection,
        "confidence",
        0.0
    )


    bbox = getattr(
        detection,
        "bbox",
        None
    )


    if bbox is None:

        continue


    # Certaines implémentations du Detector
    # retournent déjà uniquement des véhicules.
    # On ne rejette donc que les classes manifestement
    # non routières si un label existe.

    if (
        label
        and
        label not in VEHICLE_LABELS
    ):

        continue


    vehicle_count += 1


    try:

        x1, y1, x2, y2 = [
            int(value)
            for value in bbox
        ]

    except (
        TypeError,
        ValueError
    ):

        continue


    # ====================================================
    # DRAW VEHICLE
    # ====================================================

    cv2.rectangle(

        frame,

        (
            x1,
            y1
        ),

        (
            x2,
            y2
        ),

        (
            255,
            255,
            255
        ),

        2

    )


    detection_percent = (

        float(confidence)
        *
        100.0

    )


    vehicle_label = (

        f"{label or 'vehicle'} "
        f"{detection_percent:.1f}%"

    )


    cv2.putText(

        frame,

        vehicle_label,

        (
            x1,
            max(
                20,
                y1 - 8
            )
        ),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.45,

        (
            255,
            255,
            255
        ),

        1,

        cv2.LINE_AA

    )


    # ====================================================
    # ANPR
    # ====================================================

    result = plate_reader.read(

        frame,

        bbox

    )


    print(
        f"Véhicule #{vehicle_count}"
    )


    print(
        "  Type :",
        label
        or
        "vehicle"
    )


    print(
        "  Confiance détection :",
        round(
            detection_percent,
            1
        ),
        "%"
    )


    print(
        "  BBox :",
        bbox
    )


    print(
        "  ANPR status :",
        result.status
    )


    print(
        "  Texte brut :",
        result.raw_text
    )


    print(
        "  Plaque :",
        result.plate
    )


    print(
        "  Confiance OCR :",
        result.confidence,
        "%"
    )


    print()


    # ====================================================
    # ANNOTATION PLAQUE
    # ====================================================

    if result.plate:

        plate_count += 1


        text = (

            result.plate

            +
            " | "

            +
            f"{result.confidence:.1f}%"

        )


        cv2.putText(

            frame,

            text,

            (
                x1,
                min(
                    height - 10,
                    y2 + 20
                )
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.48,

            (
                255,
                255,
                255
            ),

            1,

            cv2.LINE_AA

        )


# ========================================================
# SAVE
# ========================================================

success = cv2.imwrite(

    str(
        OUTPUT_IMAGE
    ),

    frame

)


print(
    "=============================================="
)


print(
    "Véhicules analysés :",
    vehicle_count
)


print(
    "Lectures ANPR candidates :",
    plate_count
)


print(
    "Image résultat :",
    OUTPUT_IMAGE
)


if success:

    print(
        "Image résultat enregistrée : OUI"
    )

else:

    print(
        "Image résultat enregistrée : NON"
    )


print(
    "=============================================="
)

print()


if vehicle_count == 0:

    print(
        "⚠ Aucun véhicule détecté sur cette frame."
    )


elif plate_count == 0:

    print(
        "⚠ Véhicule(s) détecté(s), mais aucune "
        "plaque exploitable sur cette image."
    )


else:

    print(
        "✅ Une ou plusieurs lectures ANPR "
        "candidates ont été obtenues."
    )


print()