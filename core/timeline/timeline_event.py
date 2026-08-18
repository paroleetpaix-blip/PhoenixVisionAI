"""
========================================================
PHOENIX VISION AI

Timeline Event

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import uuid


class TimelineEvent:

    def __init__(

        self,

        event_type,

        description

    ):

        self.uuid = str(uuid.uuid4())

        self.timestamp = datetime.now()

        self.event_type = event_type

        self.description = description

    def to_dict(self):

        return {

            "uuid": self.uuid,

            "timestamp": self.timestamp.isoformat(),

            "event_type": self.event_type,

            "description": self.description

        }