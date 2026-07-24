"""
========================================================
PHOENIX VISION AI

Health Check

Vérification de l'environnement

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

import os


class HealthCheck:

    def __init__(self, detector):

        self.detector = detector

    def run(self):

        print("\n========== HEALTH CHECK ==========\n")

        ok = True

        # Vérification du modèle

        if self.detector.loaded:
            print("✓ Modèle IA chargé")
        else:
            print("✗ Modèle IA non chargé")
            ok = False

        # Vérification du dossier outputs

        if os.path.isdir("outputs"):
            print("✓ Dossier outputs")
        else:
            print("✗ Dossier outputs absent")
            ok = False

        # Vérification du dossier videos

        if os.path.isdir("videos"):
            print("✓ Dossier videos")
        else:
            print("✗ Dossier videos absent")
            ok = False

        print("\n===============================\n")

        return ok