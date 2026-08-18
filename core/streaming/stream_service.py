"""
========================================================
PHOENIX VISION AI

Streaming Service

Phoenix Security Technologies
========================================================
"""


class StreamService:

    def __init__(

        self,

        frame_hub

    ):

        self.frame_hub = frame_hub

    def latest(

        self,

        camera_id

    ):

        frame = self.frame_hub.get(

            camera_id

        )

        if frame:

            return frame.jpeg

        return None