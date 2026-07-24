"""
========================================================
PHOENIX VISION AI
engine.py

Moteur principal

Phoenix Security Technologies
SDK v0.5.0 Enterprise
========================================================
"""

from core import config
from core.utils import print_banner, ensure_directories

from core.detector import Detector
from core.tracker import Tracker
from core.counter import Counter
from core.reporter import Reporter
from core.exporter import Exporter
from core.logger import PhoenixLogger

from core.video_reader import VideoReader
from core.video_writer import VideoWriter
from core.annotator import Annotator
from core.health_check import HealthCheck


class PhoenixEngine:

    def __init__(self):

        self.status = "Initialisé"

        self.detector = Detector()
        self.tracker = Tracker()
        self.counter = Counter()
        self.reporter = Reporter()
        self.exporter = Exporter()
        self.logger = PhoenixLogger()
        self.annotator = Annotator()

    def start(self):

        print_banner()

        ensure_directories()

        print("Initialisation du moteur...")

        self.detector.load()

        health = HealthCheck(self.detector)

        if not health.run():
            raise RuntimeError(
                "Health Check échoué."
            )

        self.status = "Actif"

        self.logger.info("PhoenixEngine démarré")

        print("✓ PhoenixEngine prêt.")

    def analyze(self, source):

        if self.status != "Actif":
            raise RuntimeError(
                "Le moteur doit être démarré."
            )

        print()
        print(f"Analyse de : {source}")

        reader = VideoReader(source)
        reader.open()

        info = reader.info()

        print(
            f"Vidéo : "
            f"{info['width']}x{info['height']} "
            f"{info['fps']} FPS"
        )

        writer = VideoWriter(
            "outputs/output.mp4",
            info["fps"],
            info["width"],
            info["height"]
        )

        frame_index = 0

        self.counter.reset()

        while True:

            success, frame = reader.read()

            if not success:
                break

            detections = self.detector.detect(frame)

            tracked = self.tracker.update(
                detections
            )

            self.counter.process(tracked)

            annotated = self.annotator.draw(
                frame,
                tracked
            )

            writer.write(annotated)

            frame_index += 1

            if frame_index % 30 == 0:

                print(
                    f"Frame : "
                    f"{frame_index}/"
                    f"{info['frames']}"
                )

        reader.release()
        writer.release()

        report = self.reporter.build(
            source,
            frame_index,
            self.counter.report()
        )

        self.exporter.export_json(
            "report.json",
            report
        )

        self.logger.info(
            "Analyse terminée"
        )

        print()

        print("✓ Vidéo exportée : outputs/output.mp4")
        print("✓ Rapport JSON enregistré")

        return report

    def stop(self):

        self.detector.unload()

        self.status = "Arrêté"

        self.logger.info(
            "PhoenixEngine arrêté"
        )

        print()
        print("PhoenixEngine arrêté.")

    def get_status(self):

        return self.status