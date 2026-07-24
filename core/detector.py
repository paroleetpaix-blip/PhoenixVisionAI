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
    """
    Interface entre Phoenix Vision AI
    et les modèles d'Intelligence Artificielle.
    """

    def __init__(self):

        self.model_name = config.MODEL_NAME
        self.model_path = config.MODEL_PATH

        self.loaded = False

        self.manager = ModelManager()

    def load(self):

        print(
            f"Chargement du modèle : {self.model_name}"
        )

        self.manager.load(
            self.model_path
        )

        self.loaded = True

        print("✓ Modèle chargé.")

    def detect(self, frame):

        if not self.loaded:

            raise RuntimeError(
                "Le modèle IA n'est pas chargé."
            )

        return self.manager.predict(frame)

    def unload(self):

        self.manager.unload()

        self.loaded = False

        print("Modèle déchargé.")

    def info(self):

        return self.manager.info()