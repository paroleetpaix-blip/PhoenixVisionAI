"""
========================================================
PHOENIX VISION AI

Frame Encoder

Phoenix Security Technologies
========================================================
"""

import cv2


class FrameEncoder:

    @staticmethod
    def encode(frame):

        success, buffer = cv2.imencode(

            ".jpg",

            frame

        )

        if not success:

            return None

        return buffer.tobytes()