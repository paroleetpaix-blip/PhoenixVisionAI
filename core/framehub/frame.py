"""
========================================================
PHOENIX VISION AI

Frame

Phoenix Security Technologies
========================================================
"""


from datetime import datetime


class Frame:

    def __init__(

        self,

        camera_id,

        image

    ):

        self.camera_id = camera_id

        self.image = image

        self.timestamp = datetime.now()

class Frame:

    def __init__(

        self,

        camera_id,

        image,

        jpeg=None

    ):

        self.camera_id = camera_id

        self.image = image

        self.jpeg = jpeg

        self.timestamp = datetime.now()