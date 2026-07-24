"""
========================================================
PHOENIX VISION AI
annotator.py

Dessine les détections sur les images

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import cv2


class Annotator:

    def __init__(self):

        self.box_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.line_thickness = 2

    def draw_detection(self, frame, detection):
        """
        Dessine une seule détection.
        """

        x1, y1, x2, y2 = detection.bbox

        label = (
            f"{detection.label} "
            f"{detection.confidence:.2f}"
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            self.box_color,
            self.line_thickness
        )

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            self.text_color,
            2
        )

        return frame

    def draw(self, frame, detections):
        """
        Dessine toutes les détections d'une image.
        """

        for detection in detections:
            frame = self.draw_detection(
                frame,
                detection
            )

        return frame