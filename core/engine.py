"""
========================================================
PHOENIX VISION AI

engine.py

Moteur principal du système

Phoenix Security Technologies
Version SDK 0.4.0
========================================================
"""

from core.detector import Detector
from core.tracker import Tracker
from core.counter import Counter
from core.reporter import Reporter
from core import config
from core.utils import print_banner, ensure_directories
from core.exporter import Exporter
from core.logger import PhoenixLogger
from core.video_reader import VideoReader
from core.video_writer import VideoWriter
from core.annotator import Annotator
from core.importer import Importer


class PhoenixEngine:

    """
    Orchestrateur principal de Phoenix Vision AI.
    """


    def __init__(self):

        self.name = config.APP_NAME

        self.version = config.VERSION

        self.status = "Initialisé"


        # Modules internes

        self.detector = Detector()

        self.tracker = Tracker()

        self.counter = Counter()

        self.reporter = Reporter()

        self.exporter = Exporter()

        self.logger = PhoenixLogger()

        self.importer = Importer()

        self.annotator = Annotator()


    def start(self):

        """
        Démarre le moteur.
        """

        print_banner()

        ensure_directories()


        print("Initialisation du moteur...")


        self.detector.load()

        self.status = "Actif"

        self.logger.info("PhoenixEngine démarré")


        print("✓ PhoenixEngine prêt.")



    def analyze(self, source):

        """
        Lance une analyse complète.
        """

        if self.status != "Actif":

            raise RuntimeError(
                "Le moteur doit être démarré avant l'analyse."
            )


        print()

        print("Analyse de :", source)


        # 1 - Détection

        detections = self.detector.detect(source)



        # 2 - Tracking

        tracked_objects = self.tracker.update(
            detections
        )



        # 3 - Comptage

        self.counter.process(
            detections
        )


        report = self.reporter.build(
            source,
            tracked_objects,
            self.counter.report()
        )

        self.exporter.export_json(
            "report.json",
            report
        )

        self.logger.info(f"Analyse lancée : {source}")

        self.logger.info("Rapport JSON enregistré")

        return report



    def stop(self):

        """
        Arrête le moteur.
        """

        self.status = "Arrêté"

        self.logger.info("PhoenixEngine arrêté")

        self.detector.unload()


        print()

        print("PhoenixEngine arrêté.")



    def get_status(self):

        return self.status