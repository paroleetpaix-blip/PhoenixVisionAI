"""
========================================================
PHOENIX VISION AI
counter.py

Système de comptage des objets détectés

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""


class Counter:

    def __init__(self):
        self.reset()

    def reset(self):
        """
        Initialise les statistiques.
        """
        self.stats = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "person": 0
        }

    def add(self, detection):
        """
        Ajoute une détection au compteur.
        """

        object_name = detection.label

        if object_name in self.stats:
            self.stats[object_name] += 1

    def process(self, detections):
        """
        Traite une liste complète de détections.
        """

        self.reset()

        for detection in detections:
            self.add(detection)

        return self.stats

    def total(self):
        """
        Retourne le nombre total d'objets.
        """

        return sum(self.stats.values())

    def report(self):
        """
        Retourne un rapport structuré.
        """

        return {
            "objects": self.stats,
            "total": self.total()
        }

    def show(self):
        """
        Affichage console.
        """

        print("\n========== STATISTIQUES ==========")

        for name, value in self.stats.items():
            print(f"{name:<15}: {value}")

        print("----------------------------------")
        print(f"TOTAL            : {self.total()}")
        print("==================================")