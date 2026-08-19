"""
========================================================
PHOENIX VISION AI

Intelligence Alert

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from datetime import datetime
import uuid


class Alert:

    def __init__(
        self,
        vehicle_uuid,
        level,
        message,
        tracker_id=None,
        threat_score=0,
        alert_type="VEHICLE_THREAT"
    ):

        self.uuid = str(
            uuid.uuid4()
        )

        self.type = str(
            alert_type
        )

        self.vehicle_uuid = (
            vehicle_uuid
        )

        self.tracker_id = (
            tracker_id
        )

        self.level = str(
            level
        ).upper()

        self.message = str(
            message
        )

        self.threat_score = int(
            threat_score or 0
        )

        self.timestamp = (
            datetime.now()
        )

        self.last_seen = (
            self.timestamp
        )

        self.status = (
            "ACTIVE"
        )

        self.acknowledged_at = None

        self.resolved_at = None


    def touch(
        self,
        threat_score=None
    ):

        self.last_seen = (
            datetime.now()
        )

        if threat_score is not None:

            self.threat_score = int(
                threat_score
            )


    def acknowledge(
        self
    ):

        if self.status == "RESOLVED":

            return False

        self.status = (
            "ACKNOWLEDGED"
        )

        self.acknowledged_at = (
            datetime.now()
        )

        return True


    def resolve(
        self
    ):

        if self.status == "RESOLVED":

            return False

        self.status = (
            "RESOLVED"
        )

        self.resolved_at = (
            datetime.now()
        )

        return True


    def to_dict(
        self
    ):

        return {

            "uuid":
                self.uuid,

            "type":
                self.type,

            "vehicle_uuid":
                self.vehicle_uuid,

            "tracker_id":
                self.tracker_id,

            "level":
                self.level,

            "message":
                self.message,

            "threat_score":
                self.threat_score,

            "status":
                self.status,

            "timestamp":
                self.timestamp.isoformat(),

            "last_seen":
                self.last_seen.isoformat(),

            "acknowledged_at":
                (
                    self.acknowledged_at.isoformat()
                    if self.acknowledged_at
                    else None
                ),

            "resolved_at":
                (
                    self.resolved_at.isoformat()
                    if self.resolved_at
                    else None
                )

        }
