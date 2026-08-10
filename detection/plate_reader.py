"""
========================================================
PHOENIX VISION AI

ANPR - Plate Reader

Phoenix Security Technologies
========================================================
"""

from dataclasses import dataclass
from typing import Optional

import os
import re
import shutil
import subprocess
import tempfile

import cv2
import numpy as np


# ========================================================
# RESULTAT ANPR
# ========================================================

@dataclass
class PlateReadResult:

    detected: bool

    plate: Optional[str] = None

    raw_text: Optional[str] = None

    confidence: float = 0.0

    status: str = "NOT_DETECTED"



# ========================================================
# PLATE READER
# ========================================================

class PlateReader:

    """
    Lecteur ANPR léger pour Phoenix Vision AI V1.

    Architecture :

    Vehicle bbox
        ↓
    Crop véhicule
        ↓
    Recherche zone probable de plaque
        ↓
    Prétraitement OpenCV
        ↓
    OCR Tesseract
        ↓
    Normalisation
        ↓
    PlateReadResult

    Le moteur OCR est volontairement appelé seulement
    lorsque Phoenix décide qu'un véhicule doit être
    analysé.

    Il ne doit PAS être exécuté sur chaque frame.
    """


    def __init__(
        self,
        min_confidence=45.0,
        min_length=5,
        max_length=12
    ):

        self.min_confidence = float(
            min_confidence
        )

        self.min_length = int(
            min_length
        )

        self.max_length = int(
            max_length
        )

        self.tesseract_path = shutil.which(
            "tesseract"
        )


    # ====================================================
    # ETAT DU MOTEUR OCR
    # ====================================================

    def is_available(self):

        return (
            self.tesseract_path
            is not None
        )


    # ====================================================
    # LECTURE PRINCIPALE
    # ====================================================

    def read(
        self,
        frame,
        vehicle_bbox
    ):

        if frame is None:

            return PlateReadResult(
                detected=False,
                status="INVALID_FRAME"
            )


        if vehicle_bbox is None:

            return PlateReadResult(
                detected=False,
                status="INVALID_BBOX"
            )


        if not self.is_available():

            return PlateReadResult(
                detected=False,
                status="OCR_UNAVAILABLE"
            )


        vehicle_crop = self._crop_vehicle(

            frame,

            vehicle_bbox

        )


        if vehicle_crop is None:

            return PlateReadResult(
                detected=False,
                status="INVALID_VEHICLE_CROP"
            )


        plate_crop = self._find_plate_candidate(
            vehicle_crop
        )


        if plate_crop is None:

            plate_crop = (
                self._fallback_plate_region(
                    vehicle_crop
                )
            )


        if plate_crop is None:

            return PlateReadResult(
                detected=False,
                status="PLATE_REGION_NOT_FOUND"
            )


        processed = self._preprocess_plate(
            plate_crop
        )


        if processed is None:

            return PlateReadResult(
                detected=False,
                status="PREPROCESS_FAILED"
            )


        raw_text, confidence = (
            self._run_tesseract(
                processed
            )
        )


        if not raw_text:

            return PlateReadResult(
                detected=False,
                confidence=confidence,
                status="OCR_EMPTY"
            )


        normalized = self.normalize_plate(
            raw_text
        )


        if not normalized:

            return PlateReadResult(

                detected=False,

                raw_text=raw_text,

                confidence=confidence,

                status="INVALID_TEXT"

            )


        if confidence < self.min_confidence:

            return PlateReadResult(

                detected=False,

                plate=normalized,

                raw_text=raw_text,

                confidence=confidence,

                status="LOW_CONFIDENCE"

            )


        return PlateReadResult(

            detected=True,

            plate=normalized,

            raw_text=raw_text,

            confidence=confidence,

            status="VALIDATED"

        )


    # ====================================================
    # CROP VEHICULE
    # ====================================================

    def _crop_vehicle(
        self,
        frame,
        bbox
    ):

        try:

            height, width = (
                frame.shape[:2]
            )


            x1, y1, x2, y2 = bbox


            x1 = max(
                0,
                min(
                    int(x1),
                    width - 1
                )
            )


            y1 = max(
                0,
                min(
                    int(y1),
                    height - 1
                )
            )


            x2 = max(
                0,
                min(
                    int(x2),
                    width
                )
            )


            y2 = max(
                0,
                min(
                    int(y2),
                    height
                )
            )


            if x2 <= x1:

                return None


            if y2 <= y1:

                return None


            crop = frame[
                y1:y2,
                x1:x2
            ]


            if crop.size == 0:

                return None


            return crop


        except (
            ValueError,
            TypeError,
            AttributeError
        ):

            return None


    # ====================================================
    # DETECTION HEURISTIQUE DE PLAQUE
    # ====================================================

    def _find_plate_candidate(
        self,
        vehicle_crop
    ):

        if vehicle_crop is None:

            return None


        height, width = (
            vehicle_crop.shape[:2]
        )


        if (
            height < 30
            or
            width < 50
        ):

            return None


        # La plaque se trouve généralement dans une
        # partie basse du véhicule.
        # Il s'agit ici d'une heuristique V1,
        # pas d'un modèle spécialisé de détection.

        start_y = int(
            height * 0.30
        )


        end_y = int(
            height * 0.95
        )


        search_region = vehicle_crop[
            start_y:end_y,
            0:width
        ]


        gray = cv2.cvtColor(

            search_region,

            cv2.COLOR_BGR2GRAY

        )


        gray = cv2.bilateralFilter(

            gray,

            7,

            50,

            50

        )


        edges = cv2.Canny(

            gray,

            60,

            180

        )


        contours, _ = cv2.findContours(

            edges,

            cv2.RETR_LIST,

            cv2.CHAIN_APPROX_SIMPLE

        )


        contours = sorted(

            contours,

            key=cv2.contourArea,

            reverse=True

        )[:30]


        best_candidate = None

        best_score = 0.0


        region_area = (
            search_region.shape[0]
            *
            search_region.shape[1]
        )


        if region_area <= 0:

            return None


        for contour in contours:

            x, y, w, h = (
                cv2.boundingRect(
                    contour
                )
            )


            if h <= 0:

                continue


            aspect_ratio = (
                w / float(h)
            )


            area = (
                w * h
            )


            area_ratio = (
                area
                /
                float(region_area)
            )


            # Valeurs volontairement larges :
            # Phoenix V1 doit rester compatible avec
            # plusieurs formats de plaques.

            if not (
                1.8
                <=
                aspect_ratio
                <=
                7.0
            ):

                continue


            if area_ratio < 0.008:

                continue


            if w < 35:

                continue


            if h < 10:

                continue


            aspect_score = (

                1.0

                /

                (
                    1.0
                    +
                    abs(
                        aspect_ratio
                        -
                        4.0
                    )
                )

            )


            score = (

                area

                *
                aspect_score

            )


            if score > best_score:

                best_score = score


                padding_x = int(
                    w * 0.08
                )


                padding_y = int(
                    h * 0.18
                )


                crop_x1 = max(
                    0,
                    x - padding_x
                )


                crop_y1 = max(
                    0,
                    y - padding_y
                )


                crop_x2 = min(

                    search_region.shape[1],

                    x
                    +
                    w
                    +
                    padding_x

                )


                crop_y2 = min(

                    search_region.shape[0],

                    y
                    +
                    h
                    +
                    padding_y

                )


                best_candidate = (
                    search_region[
                        crop_y1:crop_y2,
                        crop_x1:crop_x2
                    ]
                )


        if best_candidate is None:

            return None


        if best_candidate.size == 0:

            return None


        return best_candidate


    # ====================================================
    # FALLBACK
    # ====================================================

    def _fallback_plate_region(
        self,
        vehicle_crop
    ):

        height, width = (
            vehicle_crop.shape[:2]
        )


        if (
            height < 30
            or
            width < 50
        ):

            return None


        x1 = int(
            width * 0.12
        )


        x2 = int(
            width * 0.88
        )


        y1 = int(
            height * 0.48
        )


        y2 = int(
            height * 0.92
        )


        crop = vehicle_crop[
            y1:y2,
            x1:x2
        ]


        if crop.size == 0:

            return None


        return crop


    # ====================================================
    # PRETRAITEMENT OCR
    # ====================================================

    def _preprocess_plate(
        self,
        plate_crop
    ):

        try:

            if plate_crop is None:

                return None


            if plate_crop.size == 0:

                return None


            gray = cv2.cvtColor(

                plate_crop,

                cv2.COLOR_BGR2GRAY

            )


            height, width = (
                gray.shape[:2]
            )


            if (
                height <= 0
                or
                width <= 0
            ):

                return None


            # Agrandissement modéré pour OCR.

            target_width = max(

                width * 2,

                180

            )


            scale = (

                target_width

                /
                float(width)

            )


            target_height = max(

                int(
                    height
                    *
                    scale
                ),

                50

            )


            enlarged = cv2.resize(

                gray,

                (
                    int(target_width),
                    int(target_height)
                ),

                interpolation=cv2.INTER_CUBIC

            )


            equalized = cv2.equalizeHist(
                enlarged
            )


            blurred = cv2.GaussianBlur(

                equalized,

                (3, 3),

                0

            )


            _, threshold = cv2.threshold(

                blurred,

                0,

                255,

                cv2.THRESH_BINARY
                +
                cv2.THRESH_OTSU

            )


            return threshold


        except cv2.error:

            return None


    # ====================================================
    # TESSERACT
    # ====================================================

    def _run_tesseract(
        self,
        image
    ):

        temporary_path = None


        try:

            with tempfile.NamedTemporaryFile(

                suffix=".png",

                delete=False

            ) as temporary_file:

                temporary_path = (
                    temporary_file.name
                )


            success = cv2.imwrite(

                temporary_path,

                image

            )


            if not success:

                return None, 0.0


            command = [

                self.tesseract_path,

                temporary_path,

                "stdout",

                "-l",

                "eng",

                "--oem",

                "1",

                "--psm",

                "7",

                "-c",

                (
                    "tessedit_char_whitelist="
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "0123456789"
                ),

                "tsv"

            ]


            process = subprocess.run(

                command,

                capture_output=True,

                text=True,

                timeout=4,

                check=False

            )


            if process.returncode != 0:

                return None, 0.0


            return self._parse_tesseract_tsv(
                process.stdout
            )


        except (
            subprocess.SubprocessError,
            OSError
        ):

            return None, 0.0


        finally:

            if (
                temporary_path
                and
                os.path.exists(
                    temporary_path
                )
            ):

                try:

                    os.remove(
                        temporary_path
                    )

                except OSError:

                    pass


    # ====================================================
    # TSV OCR
    # ====================================================

    def _parse_tesseract_tsv(
        self,
        tsv_text
    ):

        if not tsv_text:

            return None, 0.0


        lines = (
            tsv_text
            .strip()
            .splitlines()
        )


        if len(lines) <= 1:

            return None, 0.0


        texts = []

        confidences = []


        for line in lines[1:]:

            columns = line.split(
                "\t"
            )


            if len(columns) < 12:

                continue


            confidence_text = (
                columns[10]
            )


            text = (
                columns[11]
                .strip()
            )


            if not text:

                continue


            try:

                confidence = float(
                    confidence_text
                )

            except ValueError:

                continue


            if confidence < 0:

                continue


            texts.append(
                text
            )


            confidences.append(
                confidence
            )


        if not texts:

            return None, 0.0


        raw_text = "".join(
            texts
        )


        confidence = (

            sum(confidences)

            /

            len(confidences)

        )


        return (

            raw_text,

            round(
                confidence,
                1
            )

        )


    # ====================================================
    # NORMALISATION
    # ====================================================

    def normalize_plate(
        self,
        text
    ):

        if not text:

            return None


        text = (
            text
            .upper()
            .strip()
        )


        text = re.sub(

            r"[^A-Z0-9]",

            "",

            text

        )


        if len(text) < self.min_length:

            return None


        if len(text) > self.max_length:

            return None


        return text