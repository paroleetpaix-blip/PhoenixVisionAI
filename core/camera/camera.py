"""
========================================================
PHOENIX VISION AI

Camera Object

Phoenix Security Technologies
========================================================
"""

import uuid
from datetime import datetime

from core.camera.camera_status import CameraStatus


class Camera:

    def __init__(
        self,
        name,
        source,
        camera_type="RTSP"
    ):

        self.uuid = str(uuid.uuid4())

        self.name = name

        self.source = source

        self.camera_type = camera_type

        self.status = CameraStatus.CONNECTING

        self.width = 0

        self.height = 0

        self.fps = 0

        self.last_frame = None

        self.created_at = datetime.now()

        self.last_seen = None

        self.reconnects = 0

    def set_online(self):

        self.status = CameraStatus.ONLINE

        self.last_seen = datetime.now()

    def set_offline(self):

        self.status = CameraStatus.OFFLINE

    def increase_reconnect(self):

        self.reconnects += 1

    def to_dict(self):

        return {

            "uuid": self.uuid,

            "name": self.name,

            "source": self.source,

            "type": self.camera_type,

            "status": self.status.value,

            "fps": self.fps,

            "resolution": (

                self.width,

                self.height

            ),

            "reconnects": self.reconnects

        }