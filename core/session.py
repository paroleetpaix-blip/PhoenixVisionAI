"""
PHOENIX VISION AI

Session Manager
"""

from datetime import datetime


class Session:

    counter = 1

    def __init__(self, client="LOCAL"):

        self.client = client

        self.started_at = datetime.now()

        self.session_id = (
            f"PVAI-KIN-"
            f"{self.started_at:%Y-%m-%d}-"
            f"{Session.counter:06d}"
        )

        Session.counter += 1

    def info(self):

        return {

            "session_id": self.session_id,

            "client": self.client,

            "started_at": str(self.started_at)

        }