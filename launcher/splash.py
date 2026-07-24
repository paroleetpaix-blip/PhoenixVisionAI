"""
====================================================
PHOENIX VISION AI

Splash Screen

Phoenix Security Technologies
====================================================
"""

import time

from launcher import config



class SplashScreen:


    def show(self):

        print("\n")
        print("=" * 50)

        print(config.APP_NAME)

        print(config.VERSION)

        print("=" * 50)


        print()

        print("Powered by")

        print(config.COMPANY)

        print(config.COPYRIGHT)

        print()

        self.loading()


    def loading(self):

        steps = [

            "Chargement de la configuration",

            "Vérification de la licence",

            "Initialisation du moteur IA",

            "Initialisation du Tracker",

            "Initialisation du Reporter",

            "Préparation du système"

        ]


        for step in steps:

            print("✓", step)

            time.sleep(0.5)


        print()

        print("✓ Démarrage terminé")
