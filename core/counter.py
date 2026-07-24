"""
========================================================
PHOENIX VISION AI
counter.py

Comptage intelligent des objets

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""


class Counter:

    def __init__(self):

        self.reset()

    def reset(self):

        self.stats = {

            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "person": 0

        }

        self.total_objects = 0

    def process(self, detections):
        """
        Compte uniquement les objets
        qui n'ont jamais été comptés.
        """

        for detection in detections:

            if detection.counted:
                continue

            if detection.label in self.stats:

                self.stats[detection.label] += 1

            detection.counted = True

            self.total_objects += 1

        return self.stats

    def total(self):

        return self.total_objects

    def report(self):

        return {

            "objects": self.stats,

            "total": self.total()

        }

    def show(self):

        print("\n========== STATISTIQUES ==========")

        for name, value in self.stats.items():

            print(f"{name:<15}: {value}")

        print("----------------------------------")

        print(f"TOTAL            : {self.total()}")

        print("==================================")