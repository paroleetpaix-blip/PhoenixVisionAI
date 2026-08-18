"""
========================================================
PHOENIX VISION AI

Database Service

Phoenix Security Technologies
========================================================
"""

from core.application.service import Service


class DatabaseService(Service):

    def __init__(self):

        super().__init__("Database")

    def start(self):

        print("Connexion Base de données...")

        super().start()

    def stop(self):

        print("Déconnexion Base de données...")

        super().stop()