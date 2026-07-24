"""
========================================================
PHOENIX VISION AI

YOLO Backend Enterprise

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from core.detection import Detection


class YOLOBackend:

    def __init__(self):

        self.model = None

        self.name = "YOLOv8"

    def load(self, model_path):

        self.model = model_path

        print(f"YOLO Backend prêt : {model_path}")

    def predict(self, frame):

        """
        Version Foundation.

        Aujourd'hui :
            Simulation.

        Plus tard :
            YOLO réel (Google Colab)
            puis YOLO local.
        """

        if self.model is None:

            raise RuntimeError(
                "Aucun modèle chargé."
            )

        detections = [

            Detection(
                label="car",
                confidence=0.94,
                bbox=[120, 150, 340, 420]
            ),

            Detection(
                label="person",
                confidence=0.88,
                bbox=[520, 140, 620, 390]
            )

        ]

        return detections

    def unload(self):

        self.model = None

        print("YOLO Backend arrêté.")