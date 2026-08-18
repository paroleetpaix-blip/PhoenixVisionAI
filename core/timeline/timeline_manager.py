"""
========================================================
PHOENIX VISION AI

Timeline Manager

Phoenix Security Technologies
========================================================
"""

from core.timeline.timeline import Timeline


class TimelineManager:

    def __init__(self):

        self.timelines = {}

    def create(self, vehicle_uuid):

        self.timelines[vehicle_uuid] = Timeline()

    def exists(self, vehicle_uuid):

        return vehicle_uuid in self.timelines

    def get(self, vehicle_uuid):

        return self.timelines.get(vehicle_uuid)

    def add_event(

        self,

        vehicle_uuid,

        event_type,

        description

    ):

        if not self.exists(vehicle_uuid):

            self.create(vehicle_uuid)

        return self.get(vehicle_uuid).add(

            event_type,

            description

        )