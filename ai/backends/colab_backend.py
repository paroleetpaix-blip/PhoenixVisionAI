"""
========================================================
PHOENIX VISION AI

Google Colab Backend

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from cloud.client import CloudClient
from cloud.protocol import CloudProtocol


class ColabBackend:

    def __init__(
        self,
        server_url=None
    ):

        self.client = CloudClient(
            server_url
        )


        self.connected = False

        self.server_info = None


    # ====================================================
    # CONNECTION
    # ====================================================

    def connect(
        self
    ):

        if not self.client.is_configured():

            raise RuntimeError(

                "URL du serveur Colab absente. "
                "Définissez PHOENIX_AI_SERVER_URL."

            )


        health = (
            self.client.health()
        )


        if not isinstance(
            health,
            dict
        ):

            raise RuntimeError(
                "Réponse health invalide."
            )


        if (
            health.get(
                "status"
            )
            !=
            "online"
        ):

            raise RuntimeError(
                "Serveur IA indisponible."
            )


        self.connected = True

        self.server_info = health


        print(
            "Connexion au serveur IA établie."
        )


        print(
            "Modèle distant :",
            health.get(
                "model",
                "inconnu"
            )
        )


    # ====================================================
    # PREDICTION
    # ====================================================

    def predict(
        self,
        frame
    ):

        if not self.connected:

            raise RuntimeError(
                "Serveur IA non connecté."
            )


        response = (
            self.client
            .predict_frame(
                frame
            )
        )


        detections = (
            CloudProtocol
            .parse_prediction(
                response
            )
        )


        # Sécurité supplémentaire :
        # aucune bbox ne doit dépasser la frame.

        height, width = (
            frame.shape[:2]
        )


        for detection in detections:

            bbox = getattr(
                detection,
                "bbox",
                None
            )


            if (
                bbox is None
                or
                len(bbox) != 4
            ):

                continue


            x1, y1, x2, y2 = bbox


            x1 = max(
                0.0,
                min(
                    float(x1),
                    float(width - 1)
                )
            )


            y1 = max(
                0.0,
                min(
                    float(y1),
                    float(height - 1)
                )
            )


            x2 = max(
                0.0,
                min(
                    float(x2),
                    float(width)
                )
            )


            y2 = max(
                0.0,
                min(
                    float(y2),
                    float(height)
                )
            )


            detection.bbox = [

                x1,
                y1,
                x2,
                y2

            ]


        return detections


    # ====================================================
    # DISCONNECT
    # ====================================================

    def disconnect(
        self
    ):

        self.connected = False

        self.server_info = None


        print(
            "Connexion IA distante fermée."
        )