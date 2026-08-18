"""
========================================================
PHOENIX VISION AI

ANPR Smoke Test

Phoenix Security Technologies
========================================================
"""

from pathlib import Path

import sys


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

from pathlib import Path

import cv2
import numpy as np

import cv2
import numpy as np

from detection.plate_reader import PlateReader

from detection.plate_reader import PlateReader


# ========================================================
# OUTPUT
# ========================================================

OUTPUT_DIRECTORY = Path(
    "outputs"
)

OUTPUT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_IMAGE = (
    OUTPUT_DIRECTORY
    /
    "anpr_smoke_test.png"
)


# ========================================================
# IMAGE DE TEST
# ========================================================

frame = np.full(

    (
        360,
        640,
        3
    ),

    25,

    dtype=np.uint8

)


# ========================================================
# VEHICULE SIMULÉ
# ========================================================

vehicle_x1 = 100
vehicle_y1 = 80

vehicle_x2 = 540
vehicle_y2 = 325


cv2.rectangle(

    frame,

    (
        vehicle_x1,
        vehicle_y1
    ),

    (
        vehicle_x2,
        vehicle_y2
    ),

    (
        55,
        60,
        65
    ),

    -1

)


# ========================================================
# PLAQUE
# ========================================================

plate_x1 = 185
plate_y1 = 220

plate_x2 = 455
plate_y2 = 285


cv2.rectangle(

    frame,

    (
        plate_x1,
        plate_y1
    ),

    (
        plate_x2,
        plate_y2
    ),

    (
        245,
        245,
        245
    ),

    -1

)


cv2.rectangle(

    frame,

    (
        plate_x1,
        plate_y1
    ),

    (
        plate_x2,
        plate_y2
    ),

    (
        10,
        10,
        10
    ),

    3

)


plate_text = "2431AB01"


font = (
    cv2.FONT_HERSHEY_SIMPLEX
)

font_scale = 1.35

font_thickness = 3


text_size, _ = cv2.getTextSize(

    plate_text,

    font,

    font_scale,

    font_thickness

)


text_width = text_size[0]

text_height = text_size[1]


text_x = int(

    plate_x1

    +

    (
        (
            plate_x2
            -
            plate_x1
        )

        -
        text_width
    )

    /
    2

)


text_y = int(

    plate_y1

    +

    (
        (
            plate_y2
            -
            plate_y1
        )

        +
        text_height
    )

    /
    2

)


cv2.putText(

    frame,

    plate_text,

    (
        text_x,
        text_y
    ),

    font,

    font_scale,

    (
        0,
        0,
        0
    ),

    font_thickness,

    cv2.LINE_AA

)


# ========================================================
# SAUVEGARDE IMAGE
# ========================================================

cv2.imwrite(

    str(
        OUTPUT_IMAGE
    ),

    frame

)


# ========================================================
# PHOENIX PLATE READER
# ========================================================

reader = PlateReader(

    # Pour ce test technique uniquement,
    # on accepte toute confiance OCR afin
    # d'observer le texte réellement retourné.

    min_confidence=0.0,

    min_length=5,

    max_length=12

)


print()
print(
    "=========================================="
)

print(
    "PHOENIX ANPR SMOKE TEST"
)

print(
    "=========================================="
)

print()


print(
    "Tesseract disponible :",
    reader.is_available()
)


print(
    "Chemin Tesseract :",
    reader.tesseract_path
)


print()


result = reader.read(

    frame,

    (
        vehicle_x1,
        vehicle_y1,
        vehicle_x2,
        vehicle_y2
    )

)


print(
    "Détectée :",
    result.detected
)

print(
    "Plaque :",
    result.plate
)

print(
    "Texte OCR brut :",
    result.raw_text
)

print(
    "Confiance :",
    result.confidence
)

print(
    "Statut :",
    result.status
)

print()

print(
    "Image :",
    OUTPUT_IMAGE
)

print()


# ========================================================
# VALIDATION
# ========================================================

if result.plate == plate_text:

    print(
        "✅ TEST ANPR RÉUSSI"
    )

else:

    print(
        "⚠ ANPR actif mais lecture à ajuster"
    )


print()
