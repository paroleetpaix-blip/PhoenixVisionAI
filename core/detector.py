"""
========================================================
PHOENIX VISION AI

Detector

Gestionnaire de détection IA

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

import os

from core import config

from ai.model_manager import (
    ModelManager
)


class Detector:

    def __init__(
        self,
        backend=None
    ):

        self.model_name = (
            config.MODEL_NAME
        )

        self.model_path = (
            config.MODEL_PATH
        )


        selected_backend = (

            backend

            or

            os.getenv(
                "PHOENIX_AI_BACKEND",
                "YOLO"
            )

        )


        self.backend_name = (
            str(
                selected_backend
            )
            .strip()
            .upper()
        )


        self.loaded = False


        self.manager = (
            ModelManager(
                self.backend_name
            )
        )


    # ====================================================
    # LOAD
    # ====================================================

    def load(
        self
    ):

        if (
            self.backend_name
            ==
            "COLAB"
        ):

            print(
                "Connexion au backend IA distant : COLAB"
            )

        else:

            print(
                f"Chargement du modèle : {self.model_name}"
            )


        self.manager.load(
            self.model_path
        )


        self.loaded = True


        print(
            "✓ Moteur IA chargé."
        )


    # ====================================================
    # DETECT
    # ====================================================

    def detect(
        self,
        frame
    ):

        if not self.loaded:

            raise RuntimeError(
                "Le modèle IA n'est pas chargé."
            )


        return self.manager.predict(
            frame
        )


    # ====================================================
    # UNLOAD
    # ====================================================

    def unload(
        self
    ):

        self.manager.unload()


        self.loaded = False


        print(
            "Moteur IA déchargé."
        )


    # ====================================================
    # INFO
    # ====================================================

    def info(
        self
    ):

        return self.manager.info()