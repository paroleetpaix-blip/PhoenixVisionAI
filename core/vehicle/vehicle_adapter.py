"""
========================================================
PHOENIX VISION AI

Vehicle Adapter

Phoenix Security Technologies
========================================================
"""

from core.vehicle.vehicle import Vehicle


class VehicleAdapter:

    def __init__(self, vehicle_manager):

        self.manager = vehicle_manager

    def update(self, detections):

        vehicles = []

        for detection in detections:

            tracker_id = detection.id

            # Si le tracker ne fournit pas encore d'ID,
            # on ignore cette détection.
            if tracker_id is None:
                continue

            if self.manager.exists(tracker_id):

                vehicle = self.manager.get(tracker_id)

                vehicle.update(
                    detection.bbox
                )

            else:

                vehicle = Vehicle(

                    tracker_id,

                    detection.label,

                    detection.confidence,

                    detection.bbox

                )

            vehicles.append(vehicle)

        return vehicles
