"""
========================================================
PHOENIX VISION AI
detector.py

Gestionnaire de détection IA

Phoenix Security Technologies
========================================================
"""

from core import config
from ai.model_manager import ModelManager


class Detector:
    """
    Interface entre Phoenix Vision AI
    et les modèles d'intelligence artificielle.
    """

    def __init__(self):

        self.model = None

        self.model_name = config.MODEL_NAME

        self.model_path = config.MODEL_PATH

        self.loaded = False

        self.manager = ModelManager()


    def load(self):
        """
        Charge le modèle IA.
        """

        print(f"Chargement du modèle : {self.model_name}")

        self.model = self.manager.load(self.model_name)

        self.loaded = True

        print("✓ Modèle chargé.")

    def detect(self, source):
        """
        Lance une détection.

        Pour la version Foundation,
        nous simulons des résultats.
        """

        if not self.loaded:
            raise RuntimeError(
                "Le modèle IA n'est pas chargé."
            )

        print(f"Analyse de : {source}")

        detections = self.model.predict(source)

        print("✓ Analyse terminée.")

        return detections

    def unload(self):
        """
        Libère le modèle mémoire.
        """

        self.model = ...

        self.loaded = False

        self.manager.unload()

        print("Modèle déchargé.")