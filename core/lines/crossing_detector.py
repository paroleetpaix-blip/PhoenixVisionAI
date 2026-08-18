"""
========================================================
PHOENIX VISION AI

Crossing Detector

Détection automatique du franchissement
d'une ligne par un véhicule.

Phoenix Security Technologies
========================================================
"""


class CrossingDetector:

    def __init__(self, line_manager):

        self.line_manager = line_manager

    def process_vehicle(self, vehicle):

        previous_center = vehicle.previous_center

        if previous_center is None:
            return []

        current_center = vehicle.center

        events = []

        for line in self.line_manager.get_lines():

            direction = line.crossing_direction(
                previous_center,
                current_center
            )

            if direction is None:
                continue

            event = vehicle.register_crossing(
                line.name,
                direction
            )

            events.append(event)

        return events

        events = []

        for line in self.line_manager.get_lines():

            direction = line.crossing_direction(
                previous_center,
                current_center
            )

            if direction is None:

                continue

            event = vehicle.register_crossing(
                line.name,
                direction
            )

            events.append(event)

        return events