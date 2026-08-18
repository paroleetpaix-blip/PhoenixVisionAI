"""
========================================================
PHOENIX VISION AI

Web Service

Phoenix Security Technologies
========================================================
"""

from core.application.service import Service


class WebService(Service):

    def __init__(self):

        super().__init__("FastAPI")

    def start(self):

        print("Serveur Web prêt.")

        super().start()

    def stop(self):

        print("Serveur Web arrêté.")

        super().stop()