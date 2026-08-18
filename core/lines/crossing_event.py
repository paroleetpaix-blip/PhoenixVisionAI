"""
========================================================
PHOENIX VISION AI

Crossing Event

Événement réel de franchissement d'une ligne virtuelle.

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from datetime import datetime

import uuid


class CrossingEvent:

    def __init__(
        self,
        vehicle_uuid,
        line_name,
        direction,
        tracker_id=None
    ):

        self.uuid = str(
            uuid.uuid4()
        )

        self.type = (
            "LINE_CROSSING"
        )

        self.vehicle_uuid = (
            vehicle_uuid
        )

        self.tracker_id = (
            tracker_id
        )

        self.line_name = (
            line_name
        )

        self.direction = (
            direction
        )

        self.timestamp = (
            datetime.now()
            .isoformat()
        )

        self.level = (
            "INFO"
        )

        self.description = (
            f"Franchissement de "
            f"{line_name} "
            f"({direction})"
        )


    def warning(
        self
    ):

        self.level = (
            "WARNING"
        )


    def danger(
        self
    ):

        self.level = (
            "DANGER"
        )


    def critical(
        self
    ):

        self.level = (
            "CRITICAL"
        )


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

            "line_name":
                self.line_name,

            "direction":
                self.direction,

            "description":
                self.description,

            "timestamp":
                self.timestamp,

            "level":
                self.level

        }
