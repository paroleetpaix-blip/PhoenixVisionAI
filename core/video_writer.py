"""
========================================================
PHOENIX VISION AI
video_writer.py

Enregistrement des vidéos annotées

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import cv2


class VideoWriter:

    def __init__(self, output_path, fps, width, height):

        self.output_path = output_path

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        self.writer = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (width, height)
        )

    def write(self, frame):

        self.writer.write(frame)

    def release(self):

        self.writer.release()

    def info(self):

        return {
            "output": self.output_path
        }