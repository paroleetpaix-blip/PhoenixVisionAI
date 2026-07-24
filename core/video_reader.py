"""
========================================================
PHOENIX VISION AI
video_reader.py

Lecture des vidéos

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import cv2


class VideoReader:
    """
    Lecteur vidéo officiel de Phoenix Vision AI.
    """

    def __init__(self, path):

        self.path = path
        self.capture = None

    def open(self):

        self.capture = cv2.VideoCapture(self.path)

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Impossible d'ouvrir la vidéo : {self.path}"
            )

    def read(self):
        """
        Retourne :
            success, frame
        """
        return self.capture.read()

    def release(self):

        if self.capture is not None:
            self.capture.release()

    def fps(self):

        return int(
            self.capture.get(cv2.CAP_PROP_FPS)
        )

    def width(self):

        return int(
            self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

    def height(self):

        return int(
            self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

    def frame_count(self):

        return int(
            self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

    def duration(self):
        """
        Durée de la vidéo (secondes)
        """

        fps = self.fps()

        if fps == 0:
            return 0

        return self.frame_count() / fps

    def info(self):

        return {

            "path": self.path,

            "fps": self.fps(),

            "width": self.width(),

            "height": self.height(),

            "frames": self.frame_count(),

            "duration": round(
                self.duration(), 2
            )

        }