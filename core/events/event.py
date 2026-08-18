"""
========================================================
PHOENIX VISION AI

Event Object

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import uuid


class Event:

    def __init__(

        self,

        event_type,

        vehicle,

        description

    ):

        self.uuid = str(uuid.uuid4())

        self.type = event_type

        self.vehicle_uuid = vehicle.uuid

        self.tracker_id = vehicle.tracker_id

        self.description = description

        self.timestamp = datetime.now()

        self.level = "INFO"


    def warning(self):

        self.level = "WARNING"


    def danger(self):

        self.level = "DANGER"


    def critical(self):

        self.level = "CRITICAL"


    def to_dict(self):

        return {

            "uuid": self.uuid,

            "type": self.type,

            "vehicle_uuid": self.vehicle_uuid,

            "tracker_id": self.tracker_id,

            "description": self.description,

            "timestamp": self.timestamp.isoformat(),

            "level": self.level

        }