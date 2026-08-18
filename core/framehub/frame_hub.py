"""
========================================================
PHOENIX VISION AI

Frame Hub

Phoenix Security Technologies
========================================================
"""

from core.framehub.frame import Frame


class FrameHub:

    def __init__(self):

        self.frames = {}

    def update(

        self,

        camera_id,

        image,

        jpeg=None

    ):

        self.frames[camera_id] = Frame(

            camera_id,

            image,

            jpeg

        )

    def get(

        self,

        camera_id

    ):

        return self.frames.get(camera_id)

    def cameras(self):

        return list(

            self.frames.keys()

        )

    def total(self):

        return len(

            self.frames

        )

    def latest_jpeg(

        self,

        camera_id

    ):

        frame = self.get(

            camera_id

        )

        if frame:

            return frame.jpeg

        return None