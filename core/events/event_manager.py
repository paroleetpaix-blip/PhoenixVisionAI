"""
========================================================
PHOENIX VISION AI

Event Manager

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from datetime import (
    datetime,
    date
)

from core.events.event import Event


class EventManager:

    def __init__(
        self,
        max_events=1000
    ):

        self.events = []

        self.max_events = max(
            100,
            int(max_events)
        )

        self._known_uuids = set()


    def add(
        self,
        event
    ):

        if event is None:

            return None


        event_uuid = getattr(
            event,
            "uuid",
            None
        )


        if (
            event_uuid
            and
            event_uuid in self._known_uuids
        ):

            return event


        self.events.append(
            event
        )


        if event_uuid:

            self._known_uuids.add(
                event_uuid
            )


        self._trim()


        return event


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

        self.add(
            event
        )

        return event


    def _trim(
        self
    ):

        overflow = (
            len(self.events)
            -
            self.max_events
        )


        if overflow <= 0:

            return


        removed = self.events[
            :overflow
        ]


        self.events = self.events[
            overflow:
        ]


        for event in removed:

            event_uuid = getattr(
                event,
                "uuid",
                None
            )

            if event_uuid:

                self._known_uuids.discard(
                    event_uuid
                )


    def total(
        self
    ):

        return len(
            self.events
        )


    def all(
        self
    ):

        return list(
            self.events
        )


    def recent(
        self,
        limit=100
    ):

        limit = max(
            1,
            min(
                int(limit),
                1000
            )
        )

        return list(
            reversed(
                self.events[
                    -limit:
                ]
            )
        )


    @staticmethod
    def _event_date(
        event
    ):

        timestamp = getattr(
            event,
            "timestamp",
            None
        )


        if timestamp is None:

            return None


        if isinstance(
            timestamp,
            datetime
        ):

            return timestamp.date()


        if isinstance(
            timestamp,
            str
        ):

            try:

                return datetime.fromisoformat(
                    timestamp
                ).date()

            except ValueError:

                return None


        return None


    def today_total(
        self
    ):

        current_date = date.today()


        return sum(

            1

            for event in self.events

            if self._event_date(
                event
            )
            ==
            current_date

        )


    def level_total(
        self,
        *levels
    ):

        accepted = {
            str(level).upper()
            for level in levels
        }


        return sum(

            1

            for event in self.events

            if str(
                getattr(
                    event,
                    "level",
                    "INFO"
                )
            ).upper()
            in accepted

        )


    def stats(
        self
    ):

        return {

            "total":
                self.total(),

            "today":
                self.today_total(),

            "warnings":
                self.level_total(
                    "WARNING",
                    "DANGER"
                ),

            "critical":
                self.level_total(
                    "CRITICAL"
                )

        }


event_manager = EventManager()
