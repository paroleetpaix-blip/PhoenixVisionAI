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

from core.vehicle.vehicle_manager import VehicleManager
from core.vehicle.vehicle_adapter import VehicleAdapter

from detection.plate_reader import PlateReader

from core.zones.zone_manager import ZoneManager

from core.lines.line_manager import LineManager
from core.lines.crossing_detector import CrossingDetector

from core.memory.memory_manager import MemoryManager

from core.camera.camera_manager import CameraManager
from core.camera.reconnect_manager import ReconnectManager

from core.ui.dashboard import Dashboard

from core.framehub.frame_hub import FrameHub
from core.pipeline.pipeline import Pipeline

from core.streaming.stream_service import StreamService



from core.events.event_manager import event_manager


from core.intelligence.intelligence_center import intelligence_center


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
        self.vehicle_manager = VehicleManager()
        self.memory_manager = MemoryManager()
        
        self.vehicle_adapter = VehicleAdapter(
            self.vehicle_manager
        )

        # ======================================
        # ANPR / Plate Reader
        # ======================================
    
        self.plate_reader = PlateReader(
            min_confidence=50.0,
            min_length=5,
            max_length=12
        )

        # Sur la machine actuelle,
        # on limite fortement les appels OCR.
        self.anpr_interval_frames = 20

        # Attendre que le véhicule soit suffisamment
        # stable avant de tenter une lecture.
        self.anpr_min_vehicle_frames = 8

        # Une lecture déjà fiable n'est plus répétée.
        self.anpr_validation_confidence = 65.0

        # ======================================
        # Frame Hub
        # ======================================

        self.frame_hub = FrameHub()

        # ======================================
        # Pipeline
        # ======================================

        self.pipeline = Pipeline(
            self.frame_hub
        )

        # ======================================
        # Streaming Service
        # ======================================

        self.stream_service = StreamService(
            self.frame_hub
        )

        self.zone_manager = ZoneManager()

        self.dashboard = Dashboard()

        self.zone_manager.add_zone(

            "ZONE_TEST",

            150,

            80,

            450,

            300

        )

        self.line_manager = LineManager()

        self.line_manager.add_line(
            "ENTREE_PRINCIPALE",
            100,
            200,
            500,
            200
        )

        self.crossing_detector = CrossingDetector(
            self.line_manager
        )

        # ======================================
        # Camera Manager
        # ======================================

        self.camera_manager = CameraManager()

        self.reconnect_manager = ReconnectManager()

        

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

        camera = self.camera_manager.find_by_name("CAM01")

        if camera is None:

            raise RuntimeError(
                "CAM01 introuvable."
            )

        camera.source = source

        camera.set_online()

        reader = VideoReader(source)
        reader.open()

        info = reader.info()

        print(
            f"Vidéo : "
            f"{info['width']}x{info['height']} "
            f"{info['fps']} FPS"
        )

        camera.width = info["width"]

        camera.height = info["height"]

        camera.fps = info["fps"]

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

            # Sauvegarde de la dernière image

            camera.last_frame = frame

            detections = self.detector.detect(frame)

            tracked = self.tracker.update(
                detections
            )

            # ====================================================
            # Conversion Tracker -> Vehicle
            # ====================================================

            vehicles = self.vehicle_adapter.update(
                tracked
            )

            # ====================================================
            # ANPR - Lecture des plaques
            # ====================================================

            if self.plate_reader.is_available():

                for vehicle in vehicles:

                    # --------------------------------------------
                    # Ne plus relire une plaque déjà suffisamment
                    # fiable.
                    # --------------------------------------------

                    plate_status = getattr(
                        vehicle,
                        "plate_status",
                        "NOT_DETECTED"
                    )


                    plate_confidence = getattr(
                        vehicle,
                        "plate_confidence",
                        0.0
                    )


                    try:

                        plate_confidence = float(
                            plate_confidence
                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        plate_confidence = 0.0


                    if (
                        plate_status == "VALIDATED"
                        and
                        plate_confidence
                        >=
                        self.anpr_validation_confidence
                    ):

                        continue


                    # --------------------------------------------
                    # Laisser le tracker stabiliser le véhicule.
                    # --------------------------------------------

                    frames_seen = getattr(
                        vehicle,
                        "frames_seen",
                        1
                    )


                    if frames_seen < self.anpr_min_vehicle_frames:

                        continue


                    # --------------------------------------------
                    # OCR seulement toutes les N apparitions.
                    # --------------------------------------------

                    if (
                        frames_seen
                        %
                        self.anpr_interval_frames
                        !=
                        0
                    ):

                        continue


                    # --------------------------------------------
                    # Vérifier que le véhicule est assez grand.
                    # --------------------------------------------

                    bbox = getattr(
                        vehicle,
                        "bbox",
                        None
                    )


                    if bbox is None:

                        continue


                    try:

                        x1, y1, x2, y2 = bbox


                        vehicle_width = (
                            x2 - x1
                        )


                        vehicle_height = (
                            y2 - y1
                        )


                    except (
                        TypeError,
                        ValueError
                    ):

                        continue


                    if (
                        vehicle_width < 80
                        or
                        vehicle_height < 40
                    ):

                        continue


                    # --------------------------------------------
                    # Lecture réelle
                    # --------------------------------------------

                    result = self.plate_reader.read(

                        frame,

                        bbox

                    )


                    # --------------------------------------------
                    # Gestion du résultat ANPR
                    # --------------------------------------------

                    if result.detected:

                        # Une plaque validée passe par set_plate().
                        # Vehicle conserve automatiquement la lecture
                        # possédant la meilleure confiance.

                        vehicle.set_plate(

                            result.plate,

                            confidence=(
                                result.confidence
                            ),

                            raw_text=(
                                result.raw_text
                            ),

                            status=(
                                result.status
                            )

                        )


                        print(

                            "[PHOENIX ANPR]",

                            "Tracker:",

                            vehicle.tracker_id,

                            "| Plaque:",

                            result.plate,

                            "| OCR:",

                            f"{result.confidence:.1f}%"

                        )


                    else:

                        # Une tentative ratée ne doit jamais dégrader
                        # une plaque déjà correctement détectée.

                        if not vehicle.plate:

                            vehicle.plate_raw = (
                                result.raw_text
                            )

                            vehicle.plate_confidence = (
                                result.confidence
                            )

                            vehicle.plate_status = (
                                result.status
                            )


            # ====================================================
            # Attribution des zones aux véhicules
            # ====================================================

            for vehicle in vehicles:

                zone = self.zone_manager.find_zone(
                vehicle.center
                )

                vehicle.set_zone(zone)

                self.memory_manager.update_vehicle(
                    vehicle
                )

            # ====================================================
            # Détection des franchissements de lignes
            # ====================================================

            crossing_events = []

            for vehicle in vehicles:

                events = self.crossing_detector.process_vehicle(
                    vehicle
                )

                crossing_events.extend(events)

            # ====================================================
            # Enregistrement des événements réels
            # ====================================================

            for event in crossing_events:

                event_manager.add(
                    event
                )


            # ====================================================
            # Synchronisation de la flotte
            # ====================================================

            self.vehicle_manager.update(
                vehicles
            )

            # ====================================================
            # Intelligence / Alertes opérateur
            # ====================================================

            for vehicle in vehicles:

                alert = (
                    intelligence_center
                    .analyze_vehicle(
                        vehicle
                    )
                )


                if alert is None:

                    continue


                alert_event = (
                    event_manager.create(

                        "AI_ALERT",

                        vehicle,

                        alert.message

                    )
                )


                if alert.level == "CRITICAL":

                    alert_event.critical()

                elif alert.level == "HIGH":

                    alert_event.warning()


                print(
                    "[PHOENIX ALERT]",
                    alert.to_dict()
                )


            self.dashboard.update(

                self.camera_manager.get_all(),

                self.vehicle_manager.total(),

                intelligence_center.stats()["open"]

            )

            if frame_index % 60 == 0:

                self.dashboard.display()

            # ====================================================
            # Affichage temporaire des franchissements
            # ====================================================

            for event in crossing_events:

                print(
                    "🚨 FRANCHISSEMENT :",
                    event.to_dict()
                )

            # ====================================================
            # Statistiques véhicules
            # ====================================================

            if frame_index % 30 == 0:

                print(
                    f"Véhicules actifs : "
                    f"{self.vehicle_manager.total()}"
                )

                print(
                    f"Mémoires enregistrées : "
                    f"{self.memory_manager.total()}"
                )

            # ====================================================
            # Comptage
            # ====================================================

            self.counter.process(
                tracked
            )

            # ====================================================
            # Annotation vidéo
            # ====================================================

            annotated = self.annotator.draw(
                frame,
                tracked
            )

            # Envoi de l'image vers le Dashboard Enterprise
            self.pipeline.process(
                camera.name,
                annotated
            )

            writer.write(
                annotated
            )



            frame_index += 1

            if frame_index % 30 == 0:

                print(
                    f"Frame : "
                    f"{frame_index}/"
                    f"{info['frames']}"
                )
        camera.set_offline()
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

    def latest_frame(

        self,

        camera_id

    ):

        frame = self.frame_hub.get(

            camera_id

        )

        if frame:

            return frame.image

        return None