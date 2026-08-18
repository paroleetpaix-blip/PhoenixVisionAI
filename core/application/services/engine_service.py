"""
========================================================
PHOENIX VISION AI

Engine Service

Phoenix Security Technologies
========================================================
"""

from core.application.service import Service
from core.engine import PhoenixEngine


class EngineService(Service):

    def __init__(self):

        super().__init__("PhoenixEngine")

        self.engine = PhoenixEngine()

    def start(self):

        self.engine.start()

        super().start()

    def stop(self):

        self.engine.stop()

        super().stop()