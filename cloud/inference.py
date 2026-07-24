"""
========================================================
PHOENIX VISION AI

Cloud Inference

Phoenix Security Technologies
SDK v1.0 Enterprise
========================================================
"""

from cloud.client import CloudClient
from cloud.protocol import CloudProtocol


class CloudInference:

    def __init__(self, server_url=None):

        self.client = CloudClient(server_url)

    def predict(self, image_path):

        response = self.client.predict(image_path)

        return CloudProtocol.parse_prediction(
            response
        )