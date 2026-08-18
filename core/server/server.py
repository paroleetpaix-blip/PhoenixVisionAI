"""
========================================================
PHOENIX VISION AI

Phoenix Server

Phoenix Security Technologies
========================================================
"""

from core.server.boot_manager import BootManager

from core.server.service_manager import ServiceManager

from core.engine import PhoenixEngine

from core.server.web_server import WebServer

import threading


class PhoenixServer:

    def __init__(self):

        self.boot = BootManager()

        self.services = ServiceManager()

        self.engine = PhoenixEngine()

        self.web_server = WebServer()

    def start(self):

        self.boot.start()

        self.engine.start()

        threading.Thread(

            target=self.engine.analyze,

            args=("videos/route.mp4",),

            daemon=True

        ).start()

        self.web_server.start()

        self.services.register(

            "Phoenix Engine"

        )

        self.services.register(

            "Frame Hub"

        )

        self.services.register(

            "Pipeline"

        )

        self.services.register(
            "Web Server"
        )

        self.services.start()

        print()

        print(

            "✓ Phoenix Server prêt."

        )