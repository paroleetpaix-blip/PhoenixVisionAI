"""
========================================================
PHOENIX VISION AI

Camera Status

Phoenix Security Technologies
========================================================
"""

from enum import Enum


class CameraStatus(Enum):

    ONLINE = "ONLINE"

    OFFLINE = "OFFLINE"

    CONNECTING = "CONNECTING"

    ERROR = "ERROR"

    DISABLED = "DISABLED"

    MAINTENANCE = "MAINTENANCE"