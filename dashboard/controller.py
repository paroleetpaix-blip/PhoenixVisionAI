"""
========================================================
PHOENIX VISION AI

Dashboard Controller

Pont entre interface et moteur

Phoenix Security Technologies
========================================================
"""


from core.engine import PhoenixEngine


class DashboardController:


    def __init__(self):

        self.engine = PhoenixEngine()


    def start(self):

        self.engine.start()


    def analyze(self, source):

        return self.engine.analyze(
            source
        )


    def stop(self):

        self.engine.stop()