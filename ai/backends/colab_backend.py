"""
========================================================
PHOENIX VISION AI

Google Colab Backend

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from core.detection import Detection


class ColabBackend:

    def __init__(self):

        self.connected = False

    def connect(self):

        self.connected = True

        print("Connexion à Google Colab établie.")

    def predict(self, frame):

        if not self.connected:

            raise RuntimeError(
                "Colab non connecté."
            )

        # Simulation temporaire
        # remplacée par l'API Colab

        return [

            Detection(
                label="car",
                confidence=0.95,
                bbox=[100, 150, 320, 400]
            )

        ]

    def disconnect(self):

        self.connected = False

        print("Connexion Colab fermée.")