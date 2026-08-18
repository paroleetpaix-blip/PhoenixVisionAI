"""
========================================================
PHOENIX VISION AI

Model Manager

Gestionnaire des modèles IA

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from ai.backend_manager import BackendManager


class ModelManager:

    def __init__(
        self,
        backend_name="YOLO"
    ):

        self.backend = None

        self.backend_name = (
            str(
                backend_name
            )
            .strip()
            .upper()
        )

        self.model_name = (
            "Aucun modèle"
        )


    def load(
        self,
        model_path
    ):

        self.backend = (
            BackendManager(
                self.backend_name
            )
        )


        self.backend.load(
            model_path
        )


        if (
            self.backend_name
            ==
            "COLAB"
        ):

            self.model_name = (
                "YOLO distant"
            )

        else:

            self.model_name = (
                model_path
            )


        print(
            f"Backend : {self.backend_name}"
        )


        print(
            f"Modèle : {self.model_name}"
        )


    def predict(
        self,
        frame
    ):

        if self.backend is None:

            raise RuntimeError(
                "Aucun backend chargé."
            )


        return self.backend.predict(
            frame
        )


    def unload(
        self
    ):

        if self.backend:

            self.backend.unload()


        self.backend = None

        self.model_name = (
            "Aucun modèle"
        )


    def info(
        self
    ):

        return {

            "backend":
                self.backend_name,

            "model":
                self.model_name

        }