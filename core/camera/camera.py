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

        # ==================================================
        # LOCALISATION GÉOGRAPHIQUE
        # ==================================================

        self.site = None

        self.location_name = None

        self.address = None

        self.city = None

        self.latitude = None

        self.longitude = None

    def set_location(
        self,
        site=None,
        location_name=None,
        address=None,
        city=None,
        latitude=None,
        longitude=None
    ):

        self.site = site
        self.location_name = location_name
        self.address = address
        self.city = city

        try:
            self.latitude = (
                float(latitude)
                if latitude is not None
                else None
            )
        except (TypeError, ValueError):
            self.latitude = None

        try:
            self.longitude = (
                float(longitude)
                if longitude is not None
                else None
            )
        except (TypeError, ValueError):
            self.longitude = None


    def has_geolocation(self):

        return (
            self.latitude is not None
            and
            self.longitude is not None
        )


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

            "reconnects": self.reconnects,

            "site":
                self.site,

            "location_name":
                self.location_name,

            "address":
                self.address,

            "city":
                self.city,

            "latitude":
                self.latitude,

            "longitude":
                self.longitude,

            "gps_configured":
                self.has_geolocation()

        }