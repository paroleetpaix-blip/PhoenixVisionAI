"""
========================================================
PHOENIX VISION AI

Frame Stream

Phoenix Security Technologies
========================================================
"""


class FrameStream:

    def __init__(

        self,

        hub

    ):

        self.hub = hub

    def latest(

        self,

        camera_id

    ):

        frame = self.hub.get(

            camera_id

        )

        if frame:

            return frame.image

        return None

    def latest_jpeg(

        self,

        camera_id

    ):

        frame = self.hub.get(

            camera_id

        )

        if frame:

            return frame.jpeg

        return None