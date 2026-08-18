from datetime import datetime
import uuid


class Alert:

    def __init__(

        self,

        vehicle_uuid,

        level,

        message

    ):

        self.uuid = str(uuid.uuid4())

        self.vehicle_uuid = vehicle_uuid

        self.level = level

        self.message = message

        self.timestamp = datetime.now()

    def to_dict(self):

        return {

            "uuid": self.uuid,

            "vehicle_uuid": self.vehicle_uuid,

            "level": self.level,

            "message": self.message,

            "timestamp": self.timestamp.isoformat()

        }