"""
========================================================
PHOENIX VISION AI

Journey

Phoenix Security Technologies
========================================================
"""

from datetime import datetime


class Journey:

    def __init__(self, vehicle_uuid):

        self.vehicle_uuid = vehicle_uuid

        self.points = []


    def add(

        self,

        camera,

        zone,

        center

    ):

        self.points.append({

            "timestamp": datetime.now(),

            "camera": camera,

            "zone": zone,

            "center": center

        })


    def total(self):

        return len(self.points)


    def export(self):

        return self.points