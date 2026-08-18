"""
========================================================
PHOENIX VISION AI

Dashboard

Phoenix Security Technologies
========================================================
"""


class Dashboard:


    def __init__(self):

        self.cameras = []

        self.vehicles = 0

        self.alerts = 0

        self.status = "READY"



    def update(

        self,

        cameras,

        vehicles,

        alerts

    ):

        self.cameras = cameras

        self.vehicles = vehicles

        self.alerts = alerts



    def display(self):


        print()

        print("=" * 70)

        print(
            "          PHOENIX VISION AI DASHBOARD"
        )

        print("=" * 70)


        print()

        print(
            f"Caméras : {len(self.cameras)}"
        )


        print(
            f"Véhicules suivis : {self.vehicles}"
        )


        print(
            f"Alertes : {self.alerts}"
        )


        print()

        print("-" * 70)

        print("CAMERAS")

        print("-" * 70)



        for camera in self.cameras:


            data = camera.to_dict()


            print(

                f"{data['name']} | "

                f"{data['status']} | "

                f"{data['type']}"

            )


        print()

        print("=" * 70)

        print()