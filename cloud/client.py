"""
========================================================
PHOENIX VISION AI

Cloud Client

Communication avec le serveur IA

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from cloud.settings import SERVER_URL, TIMEOUT
import requests


class CloudClient:

    def __init__(self, server_url=None):

        self.server_url = (
            server_url or SERVER_URL
        ).rstrip("/")

    def health(self):

        """
        Vérifie si le serveur IA répond.
        """

        response = requests.get(
            f"{self.server_url}/health",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    def predict(self, image_path):

        """
        Envoie une image au serveur IA.
        """

        with open(image_path, "rb") as image:

            files = {

                "image": image

            }

            response = requests.post(

                f"{self.server_url}/predict",

                files=files,

                timeout=TIMEOUT

            )

        response.raise_for_status()

        return response.json()