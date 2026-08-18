"""
========================================================
PHOENIX VISION AI

Crossing Event

Événement de franchissement d'une ligne virtuelle.

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import uuid


class CrossingEvent:

    def __init__(
        self,
        vehicle_uuid,
        line_name,
        direction
    ):

        self.uuid = str(uuid.uuid4())

        self.vehicle_uuid = vehicle_uuid

        self.line_name = line_name

        self.direction = direction

        self.timestamp = datetime.now().isoformat()

    def to_dict(self):

        return {
            "uuid": self.uuid,
            "vehicle_uuid": self.vehicle_uuid,
            "line_name": self.line_name,
            "direction": self.direction,
            "timestamp": self.timestamp
        }