"""
========================================================
PHOENIX VISION AI

Backend Manager

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from ai.backends.yolo_backend import YOLOBackend
from ai.backends.colab_backend import ColabBackend


class BackendManager:

    def __init__(self, backend="YOLO"):

        self.backend_name = backend.upper()

        if self.backend_name == "YOLO":

            self.backend = YOLOBackend()

        elif self.backend_name == "COLAB":

            self.backend = ColabBackend()

        else:

            raise ValueError(
                f"Backend inconnu : {backend}"
            )

    def load(self, model_path):

        if self.backend_name == "YOLO":

            self.backend.load(model_path)

        elif self.backend_name == "COLAB":

            self.backend.connect()

    def predict(self, frame):

        return self.backend.predict(frame)

    def unload(self):

        if self.backend_name == "YOLO":

            self.backend.unload()

        elif self.backend_name == "COLAB":

            self.backend.disconnect()