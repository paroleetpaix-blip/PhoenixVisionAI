"""
========================================================
PHOENIX VISION AI

Journey Manager

Phoenix Security Technologies
========================================================
"""

from core.journey.journey import Journey


class JourneyManager:

    def __init__(self):

        self.journeys = {}


    def get(self, uuid):

        if uuid not in self.journeys:

            self.journeys[uuid] = Journey(uuid)

        return self.journeys[uuid]


    def add_position(

        self,

        vehicle,

        camera_name

    ):

        journey = self.get(vehicle.uuid)

        journey.add(

            camera_name,

            vehicle.zone,

            vehicle.center

        )


    def total(self):

        return len(self.journeys)