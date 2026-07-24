"""
========================================================
PHOENIX VISION AI
detector.py

Gestionnaire de détection IA

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from core import config
from ai.model_manager import ModelManager


class Detector:

    def __init__(self):

        self.manager = ModelManager()

        self.model = None

        self.loaded = False

        self.model_name = config.MODEL_NAME


    def load(self):

        print(f"Chargement du modèle : {self.model_name}")

        self.model = self.manager.load(self.model_name)

        self.loaded = True

        print("✓ Modèle chargé.")


    def detect(self, source):

        if not self.loaded:

            raise RuntimeError(
                "Le modèle IA n'est pas chargé."
            )

        print(f"Analyse de : {source}")

        detections = self.model.predict(source)

        print("✓ Analyse terminée.")

        return detections


    def unload(self):

        self.manager.unload()

        self.model = None

        self.loaded = False

        print("Modèle déchargé.")