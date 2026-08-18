"""
========================================================
PHOENIX VISION AI

Cloud Inference

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from cloud.client import CloudClient
from cloud.protocol import CloudProtocol


class CloudInference:

    def __init__(
        self,
        server_url=None
    ):

        self.client = CloudClient(
            server_url
        )


    def health(
        self
    ):

        return self.client.health()


    def predict(
        self,
        image_path
    ):

        response = self.client.predict(
            image_path
        )


        return (
            CloudProtocol
            .parse_prediction(
                response
            )
        )


    def predict_frame(
        self,
        frame
    ):

        response = (
            self.client
            .predict_frame(
                frame
            )
        )


        return (
            CloudProtocol
            .parse_prediction(
                response
            )
        )