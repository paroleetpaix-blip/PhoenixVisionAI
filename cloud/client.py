"""
========================================================
PHOENIX VISION AI

Cloud Client

Communication avec le serveur IA distant

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from pathlib import Path

import cv2
import requests

from cloud.settings import (
    SERVER_URL,
    API_KEY,
    TIMEOUT,
    JPEG_QUALITY
)


class CloudClient:

    def __init__(
        self,
        server_url=None
    ):

        self.server_url = (

            server_url
            or
            SERVER_URL

        ).strip().rstrip("/")


    # ====================================================
    # CONFIGURATION
    # ====================================================

    def is_configured(
        self
    ):

        return bool(
            self.server_url
        )


    def _ensure_configured(
        self
    ):

        if not self.is_configured():

            raise RuntimeError(

                "Serveur IA non configuré. "
                "Définissez PHOENIX_AI_SERVER_URL."

            )


    def _headers(
        self
    ):

        headers = {}


        if API_KEY:

            headers[
                "Authorization"
            ] = (
                f"Bearer {API_KEY}"
            )


        return headers


    # ====================================================
    # HEALTH
    # ====================================================

    def health(
        self
    ):

        self._ensure_configured()


        response = requests.get(

            f"{self.server_url}/health",

            headers=self._headers(),

            timeout=TIMEOUT

        )


        response.raise_for_status()


        return response.json()


    # ====================================================
    # PREDICT FILE
    # Compatibility with the old API
    # ====================================================

    def predict(
        self,
        image_path
    ):

        self._ensure_configured()


        image_path = Path(
            image_path
        )


        if not image_path.exists():

            raise FileNotFoundError(
                image_path
            )


        with image_path.open(
            "rb"
        ) as image:

            files = {

                "image": (

                    image_path.name,

                    image,

                    "image/jpeg"

                )

            }


            response = requests.post(

                f"{self.server_url}/predict",

                files=files,

                headers=self._headers(),

                timeout=TIMEOUT

            )


        response.raise_for_status()


        return response.json()


    # ====================================================
    # PREDICT OPENCV FRAME
    # ====================================================

    def predict_frame(
        self,
        frame
    ):

        self._ensure_configured()


        if frame is None:

            raise ValueError(
                "Frame IA absente."
            )


        parameters = [

            int(
                cv2.IMWRITE_JPEG_QUALITY
            ),

            JPEG_QUALITY

        ]


        success, encoded = (
            cv2.imencode(
                ".jpg",
                frame,
                parameters
            )
        )


        if not success:

            raise RuntimeError(
                "Encodage JPEG impossible."
            )


        files = {

            "image": (

                "phoenix_frame.jpg",

                encoded.tobytes(),

                "image/jpeg"

            )

        }


        response = requests.post(

            f"{self.server_url}/predict",

            files=files,

            headers=self._headers(),

            timeout=TIMEOUT

        )


        response.raise_for_status()


        return response.json()