"""
========================================================
PHOENIX VISION AI

Importer

Lecture des résultats provenant
de Google Colab ou d'autres moteurs IA.

Phoenix Security Technologies
========================================================
"""

import json
from core.detection import Detection


class Importer:

    def load_json(self, path):

        with open(path, "r", encoding="utf-8") as file:

            data = json.load(file)

        detections = []

        for item in data:

            detections.append(

                Detection(
                    label=item["label"],
                    confidence=item["confidence"],
                    bbox=item["bbox"]
                )

            )

        return detections