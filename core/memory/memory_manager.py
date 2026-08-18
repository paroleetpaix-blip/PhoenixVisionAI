from core.memory.vehicle_memory import VehicleMemory

class MemoryManager:

    def __init__(self):

        self.memories = {}

    def exists(self, uuid):

        return uuid in self.memories

    def get(self, uuid):

        return self.memories.get(uuid)

    def total(self):

        return len(self.memories)

    def update_vehicle(self, vehicle):

        if vehicle.uuid not in self.memories:

            self.memories[vehicle.uuid] = VehicleMemory(
                vehicle
            )

        self.memories[vehicle.uuid].update(vehicle)

    def get_memory(self, uuid):

        return self.memories.get(uuid)