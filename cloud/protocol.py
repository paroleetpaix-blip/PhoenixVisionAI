"""
========================================================
PHOENIX VISION AI

Cloud Protocol

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from core.detection import Detection


class CloudProtocol:

    @staticmethod
    def parse_prediction(response):

        detections = []

        for item in response.get("detections", []):

            detection = Detection(

                label=item["label"],

                confidence=item["confidence"],

                bbox=item["bbox"]

            )

            detections.append(detection)

        return detections