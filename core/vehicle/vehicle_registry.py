"""
========================================================
PHOENIX VISION AI

Vehicle Registry

Mémoire permanente des véhicules.

Phoenix Security Technologies
========================================================
"""


class VehicleRegistry:

    def __init__(self):

        self.registry = {}


    def register(self, vehicle):

        self.registry[vehicle.uuid] = vehicle


    def exists(self, uuid):

        return uuid in self.registry


    def get(self, uuid):

        return self.registry.get(uuid)


    def total(self):

        return len(self.registry)


    def all(self):

        return list(self.registry.values())