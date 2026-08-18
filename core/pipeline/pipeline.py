"""
========================================================
PHOENIX VISION AI

Pipeline

Phoenix Security Technologies
========================================================
"""

from core.pipeline.frame_encoder import FrameEncoder

class Pipeline:

    def __init__(

        self,

        frame_hub

    ):

        self.frame_hub = frame_hub

    def process(

        self,

        camera_id,

        frame

    ):
        jpeg = FrameEncoder.encode(

            frame

        )

        self.frame_hub.update(

            camera_id,

            frame,

            jpeg

        )

        return frame