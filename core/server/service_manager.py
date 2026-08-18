"""
========================================================
PHOENIX VISION AI

Service Manager

Phoenix Security Technologies
========================================================
"""


class ServiceManager:

    def __init__(self):

        self.services = []

    def register(

        self,

        service

    ):

        self.services.append(service)

    def start(self):

        for service in self.services:

            print(

                f"✓ {service}"

            )