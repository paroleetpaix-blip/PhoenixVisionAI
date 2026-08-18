"""
========================================================
PHOENIX VISION AI

Evidence Object

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import uuid


class Evidence:

    def __init__(

        self,

        vehicle_uuid,

        event_type,

        image_path

    ):

        self.uuid = str(uuid.uuid4())

        self.vehicle_uuid = vehicle_uuid

        self.event_type = event_type

        self.image_path = image_path

        self.timestamp = datetime.now()

    def to_dict(self):

        return {

            "uuid": self.uuid,

            "vehicle_uuid": self.vehicle_uuid,

            "event_type": self.event_type,

            "image_path": self.image_path,

            "timestamp": self.timestamp.isoformat()

        }