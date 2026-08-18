"""
========================================================
PHOENIX VISION AI

Timeline

Phoenix Security Technologies
========================================================
"""

from core.timeline.timeline_event import TimelineEvent


class Timeline:

    def __init__(self):

        self.events = []

    def add(

        self,

        event_type,

        description

    ):

        event = TimelineEvent(

            event_type,

            description

        )

        self.events.append(event)

        return event

    def total(self):

        return len(self.events)

    def export(self):

        return [

            event.to_dict()

            for event in self.events

        ]