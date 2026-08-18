"""
========================================================
PHOENIX VISION AI

Web Server

Phoenix Security Technologies
========================================================
"""

import threading
import uvicorn
from core.server.port_manager import PortManager


class WebServer:

    def __init__(

        self,

        host="127.0.0.1",

        port=8000

    ):

        self.host = host

        self.port = PortManager.find_available(

            host,

            port

        )

        self.thread = None

    def start(self):

        if self.thread is not None:

            return

        def run():

            uvicorn.run(

                "web.app:app",

                host=self.host,

                port=self.port,

                reload=False

            )

        self.thread = threading.Thread(

            target=run,

            daemon=True

        )

        self.thread.start()

        print(

            f"✓ Web Server : http://{self.host}:{self.port}"

        )
