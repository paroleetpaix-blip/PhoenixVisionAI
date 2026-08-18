"""
========================================================
PHOENIX VISION AI

Event Manager

Phoenix Security Technologies
========================================================
"""

from core.events.event import Event


class EventManager:

    def __init__(self):

        self.events = []


    def create(

        self,

        event_type,

        vehicle,

        description

    ):

        event = Event(

            event_type,

            vehicle,

            description

        )

        self.events.append(event)

        return event


    def total(self):

        return len(self.events)


    def all(self):

        return self.events