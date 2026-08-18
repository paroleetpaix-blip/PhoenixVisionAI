"""
========================================================
PHOENIX VISION AI

Zone Manager

Phoenix Security Technologies
========================================================
"""

from core.zones.zone import Zone


class ZoneManager:

    def __init__(self):

        self.zones = []

    def add_zone(

        self,

        name,

        x1,

        y1,

        x2,

        y2

    ):

        zone = Zone(

            name,

            x1,

            y1,

            x2,

            y2

        )

        self.zones.append(zone)

    def get_zones(self):

        return self.zones

    def find_zone(self, point):

        for zone in self.zones:

            if zone.contains(point):

                return zone

        return None