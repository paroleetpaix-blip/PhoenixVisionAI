"""
========================================================
PHOENIX VISION AI

Camera Grid Engine

Phoenix Security Technologies
========================================================
"""

from core.display.camera_layout import CameraLayout


class CameraGridEngine:

    def __init__(self):

        self.cameras = []

    def set_cameras(self, cameras):

        self.cameras = cameras

    def total(self):

        return len(self.cameras)

    def layout(self):

        return CameraLayout.get_layout(

            self.total()

        )

    def visible_cameras(self):

        return self.cameras