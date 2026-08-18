"""
========================================================
PHOENIX VISION AI

Port Manager

Phoenix Security Technologies
========================================================
"""

import socket


class PortManager:

    @staticmethod
    def is_available(host, port):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:

            sock.bind((host, port))

            sock.close()

            return True

        except OSError:

            return False

    @staticmethod
    def find_available(

        host="127.0.0.1",

        start=8000,

        end=8010

    ):

        for port in range(start, end + 1):

            if PortManager.is_available(

                host,

                port

            ):

                return port

        raise RuntimeError(

            "Aucun port disponible."
        )