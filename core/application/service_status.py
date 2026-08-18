"""
========================================================
PHOENIX VISION AI

Service Status

Phoenix Security Technologies
========================================================
"""

from enum import Enum


class ServiceStatus(Enum):

    STOPPED = "STOPPED"

    STARTING = "STARTING"

    RUNNING = "RUNNING"

    STOPPING = "STOPPING"

    ERROR = "ERROR"