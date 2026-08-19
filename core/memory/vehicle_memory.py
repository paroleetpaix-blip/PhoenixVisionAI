from datetime import datetime


class VehicleMemory:

    def __init__(self, vehicle):

        self.uuid = vehicle.uuid

        self.first_seen = datetime.now()

        self.last_seen = datetime.now()

        self.total_frames = 0

        self.max_speed = 0

        self.max_threat = 0

        self.zones = []

        self.crossings = []

        self.alerts = []

        self.positions = []

        self.speed_history = []

        self.zone_history = []

        self.direction_history = []

        self.status_history = []

        self.threat_history = []

        self.time_in_system = 0

        self.last_camera = None

        self.cameras_seen = []

    def update(self, vehicle):

        self.last_seen = datetime.now()

        self.total_frames += 1

        self.max_speed = max(
            self.max_speed,
            vehicle.speed
        )

        self.max_threat = max(
            self.max_threat,
            vehicle.threat_score
        )

        self.positions.append(
            vehicle.center
        )

        self.speed_history.append(
            vehicle.speed
        )

        self.direction_history.append(
            vehicle.direction
        )

        self.status_history.append(
            vehicle.status
        )

        self.threat_history.append(
            vehicle.threat_score
        )

        if vehicle.zone:

            if (
                not self.zone_history
                or
                self.zone_history[-1]
                !=
                vehicle.zone
            ):

                self.zone_history.append(
                    vehicle.zone
                )


            self.time_in_system += 1

    def set_camera(self, camera_name):

        self.last_camera = camera_name

        if camera_name not in self.cameras_seen:

            self.cameras_seen.append(
                camera_name
            )

    def summary(self):

        return {

            "uuid": self.uuid,

            "first_seen": self.first_seen,

            "last_seen": self.last_seen,

            "frames": self.total_frames,

            "max_speed": self.max_speed,

            "max_threat": self.max_threat,

            "zones": self.zone_history,

            "cameras": self.cameras_seen,

            "alerts": len(self.alerts)

        }