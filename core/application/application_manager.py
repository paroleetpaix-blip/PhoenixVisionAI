"""
========================================================
PHOENIX VISION AI

Application Manager

Phoenix Security Technologies

Enterprise Core
========================================================
"""

from core.application.service import Service


class ApplicationManager:

    def __init__(self):

        self.services = {}

    def register(

        self,

        service: Service

    ):

        self.services[service.name] = service

    def get(

        self,

        name

    ):

        return self.services.get(name)

    def start_all(self):

        for service in self.services.values():

            service.start()

    def stop_all(self):

        for service in self.services.values():

            service.stop()

    def running_services(self):

        return [

            service.info()

            for service in self.services.values()

        ]

    def total(self):

        return len(self.services)

    def report(self):

        print()

        print("===== APPLICATION SERVICES =====")

        for service in self.services.values():

            print(

                f"{service.name:<20}"

                f"{service.status.value}"

            )

        print()