"""
========================================================
PHOENIX VISION AI
detection.py

Objet Detection

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""


class Detection:
    """
    Représente une détection unique.
    """

    def __init__(
        self,
        label,
        confidence,
        bbox,
        object_id=None,
        timestamp=None
    ):

        self.id = object_id

        self.label = label

        self.confidence = float(confidence)

        self.bbox = bbox

        self.timestamp = timestamp

        self.counted = False

    def to_dict(self):

        return {

            "id": self.id,

            "label": self.label,

            "confidence": round(
                self.confidence,
                3
            ),

            "bbox": self.bbox,

            "timestamp": self.timestamp,

            "counted": self.counted

        }

    def __repr__(self):

        return (
            f"Detection("
            f"id={self.id}, "
            f"label='{self.label}', "
            f"confidence={self.confidence:.2f})"
        )