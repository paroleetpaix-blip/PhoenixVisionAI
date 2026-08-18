"""
========================================================
PHOENIX VISION AI

Vehicle Manager

Phoenix Security Technologies
========================================================
"""

from core.vehicle.vehicle import Vehicle


class VehicleManager:

    def __init__(self):

        self.vehicles = {}


    def create_vehicle(
        self,
        tracker_id,
        label,
        confidence,
        bbox
    ):

        vehicle = Vehicle(

            tracker_id,

            label,

            confidence,

            bbox

        )

        self.vehicles[tracker_id] = vehicle

        return vehicle


    def exists(self, tracker_id):

        return tracker_id in self.vehicles


    def get(self, tracker_id):

        return self.vehicles.get(tracker_id)


    def update_vehicle(
        self,
        tracker_id,
        bbox
    ):

        vehicle = self.get(tracker_id)

        if vehicle:

            vehicle.update(bbox)

    def update(self, vehicles):

        """
        Synchronise les véhicules actifs avec
        les véhicules présents sur la frame courante.
        """

        current_ids = set()


        for vehicle in vehicles:

            tracker_id = vehicle.tracker_id

            current_ids.add(
                tracker_id
            )


            if not self.exists(
                tracker_id
            ):

                self.vehicles[
                    tracker_id
                ] = vehicle


        # Supprimer les véhicules qui
        # ne sont plus présents sur la frame

        previous_ids = set(
            self.vehicles.keys()
        )


        disappeared = (
            previous_ids
            -
            current_ids
        )


        for tracker_id in disappeared:

            self.remove_vehicle(
                tracker_id
            )


    def remove_vehicle(self, tracker_id):

        if tracker_id in self.vehicles:

            del self.vehicles[tracker_id]


    def total(self):

        return len(self.vehicles)


    def all(self):

        return list(self.vehicles.values())

        # ---------------------------------
    # Premier véhicule actif
    # ---------------------------------

    def current_vehicle(self):

        vehicles = self.all()

        if len(vehicles) == 0:

            return None

        return vehicles[0]