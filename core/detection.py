"""
========================================================
PHOENIX VISION AI

Detection Object

Format standard des objets détectés.

Phoenix Security Technologies
========================================================
"""


class Detection:


    def __init__(
        self,
        label,
        confidence,
        bbox=None
    ):

        self.label = label

        self.confidence = confidence

        self.bbox = bbox



    def to_dict(self):

        return {

            "label": self.label,

            "confidence": self.confidence,

            "bbox": self.bbox

        }