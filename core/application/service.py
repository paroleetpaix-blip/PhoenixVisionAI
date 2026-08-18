"""
========================================================
PHOENIX VISION AI

Generic Service

Phoenix Security Technologies
========================================================
"""

from core.application.service_status import ServiceStatus


class Service:

    def __init__(

        self,

        name

    ):

        self.name = name

        self.status = ServiceStatus.STOPPED

    def start(self):

        self.status = ServiceStatus.RUNNING

    def stop(self):

        self.status = ServiceStatus.STOPPED

    def is_running(self):

        return self.status == ServiceStatus.RUNNING

    def info(self):

        return {

            "name": self.name,

            "status": self.status.value

        }