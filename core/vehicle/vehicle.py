"""
========================================================
PHOENIX VISION AI

Vehicle Object

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import uuid
from core.lines.crossing_event import CrossingEvent


class Vehicle:

    def __init__(
        self,
        tracker_id,
        label,
        confidence,
        bbox
    ):

        # Identifiant interne unique

        self.uuid = str(uuid.uuid4())

        # Tracker

        self.tracker_id = tracker_id

        # Détection IA

        self.label = label

        self.confidence = confidence

        self.bbox = bbox

        # Position

        self.previous_bbox = bbox

        self.center = self.compute_center(bbox)


        # Mouvement

        self.distance = 0.0

        self.stationary_frames = 0

        self.is_stationary = False

        # Informations ANPR

        self.plate = None

        self.plate_raw = None

        self.plate_confidence = 0.0

        self.plate_status = "NOT_DETECTED"

        self.plate_last_seen = None
        
        # Informations véhicule

        self.color = None

        self.brand = None

        self.model = None

        # Mouvement

        self.direction = None

        self.previous_direction = None

        self.uturn_detected = False

        self.speed = 0.0

        # Historique

        self.first_seen = datetime.now()

        self.last_seen = datetime.now()

        self.frames_seen = 1

        self.previous_center = None

        self.history = []

        self.crossing_events = []

        # État

        self.status = "NORMAL"

        self.threat_score = 0

        self.threat_level = "LOW"

        self.notes = ""

        self.zone = None

    
    def update(self, bbox):

        self.previous_bbox = self.bbox

        self.previous_center = self.center

        self.bbox = bbox

        self.center = self.compute_center(bbox)

        self.history.append(self.center)

        if len(self.history) > 300:

            self.history.pop(0)

        self.distance = self.compute_distance()

        self.speed = self.compute_speed()

        self.previous_direction = self.direction

        self.direction = self.compute_direction()

        self.detect_uturn()

        if self.distance < 3:

            self.stationary_frames += 1

        else:

            self.stationary_frames = 0

        self.evaluate_threat()

        self.is_stationary = self.stationary_frames > 15

        self.frames_seen += 1

        self.last_seen = datetime.now()

    def set_plate(

        self,

        plate,

        confidence=0.0,

        raw_text=None,

        status="VALIDATED"

    ):

        if not plate:

            return False


        try:

            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0


        # Si Phoenix possède déjà une lecture plus fiable,
        # on ne la remplace pas par une lecture moins fiable.

        if (

            self.plate

            and

            confidence
            <
            self.plate_confidence

        ):

            return False


        self.plate = str(
            plate
        )


        self.plate_raw = (

            str(raw_text)

            if raw_text is not None

            else self.plate

        )


        self.plate_confidence = round(

            confidence,

            1

        )


        self.plate_status = str(
            status
        )


        self.plate_last_seen = (
            datetime.now()
        )


        return True

    def set_color(self, color):

        self.color = color

    def set_brand(self, brand):

        self.brand = brand

    def set_model(self, model):

        self.model = model

    def mark_suspicious(self):

        self.status = "SUSPICIOUS"

    def mark_wanted(self):

        self.status = "WANTED"
    
    def compute_center(self, bbox):

        x1, y1, x2, y2 = bbox

        return (

            (x1 + x2) / 2,

            (y1 + y2) / 2
        
        )
    
    def compute_distance(self):

        x1, y1 = self.previous_center

        x2, y2 = self.center

        dx = x2 - x1

        dy = y2 - y1

        return (dx**2 + dy**2) ** 0.5
    
    def get_center(self):

        return self.center


    def get_width(self):

        x1, _, x2, _ = self.bbox

        return x2 - x1

    def get_height(self):

        _, y1, _, y2 = self.bbox

        return y2 - y1

    def area(self):

        return self.get_width() * self.get_height()

    def compute_direction(self):

        x1, y1 = self.previous_center

        x2, y2 = self.center

        dx = x2 - x1

        dy = y2 - y1

        threshold = 2

        if abs(dx) < threshold and abs(dy) < threshold:
            return "STATIONARY"

        if abs(dx) > abs(dy):

            if dx > 0:
                return "EAST"

            return "WEST"

        else:

            if dy > 0:
                return "SOUTH"

            return "NORTH"

    def compute_speed(self):

        """
        Vitesse relative en pixels/frame.
        """

        return round(self.distance, 2)

    def detect_uturn(self):

        if self.previous_direction is None:
            return

        opposite = {

            "EAST": "WEST",
            "WEST": "EAST",
            "NORTH": "SOUTH",
            "SOUTH": "NORTH"

        }

        if self.previous_direction in opposite:

            if self.direction == opposite[self.previous_direction]:

                self.uturn_detected = True

    def evaluate_threat(self):

        score = 0

        # Véhicule recherché
        if self.status == "WANTED":
            score += 100

        # Véhicule suspect
        elif self.status == "SUSPICIOUS":
            score += 40

        # Demi-tour détecté
        if self.uturn_detected:
            score += 20

        # Véhicule arrêté longtemps
        if self.is_stationary:
            score += 15

        # Vitesse élevée
        if self.speed > 20:
            score += 10

        self.threat_score = min(score, 100)

        if self.threat_score >= 80:
            self.threat_level = "CRITICAL"

        elif self.threat_score >= 50:
            self.threat_level = "HIGH"

        elif self.threat_score >= 20:
            self.threat_level = "MEDIUM"

        else:
            self.threat_level = "LOW"

    def movement_status(self):

        if self.is_stationary:

            return "STOPPED"
        
        if self.speed > 15:

            return "FAST"

        if self.speed > 3:

            return "MOVING"

        return "SLOW"

    def set_zone(self, zone):

        if zone:

            self.zone = zone.name

        else:

            self.zone = None

    def update_center_history(self):

        current_center = self.center

        if self.previous_center is None:

            self.previous_center = current_center

            return None

        previous_center = self.previous_center

        self.previous_center = current_center

        return previous_center

    def register_crossing(
        self,
        line_name,
        direction
    ):

        event = CrossingEvent(
            self.uuid,
            line_name,
            direction
        )

        self.crossing_events.append(event)

        return event

    def to_dict(self):

        return {

            "uuid": self.uuid,

            "tracker_id": self.tracker_id,

            "label": self.label,

            "confidence": self.confidence,

            "bbox": self.bbox,

            "plate":
                self.plate,

            "plate_raw":
                self.plate_raw,

            "plate_confidence":
                self.plate_confidence,

            "plate_status":
                self.plate_status,

            "plate_last_seen":
                (
                    self.plate_last_seen.isoformat()
                    if self.plate_last_seen
                    else None
                ),

            "color":
                self.color,

            "brand": self.brand,

            "model": self.model,

            "direction": self.direction,

            "uturn_detected": self.uturn_detected,

            "zone": self.zone,

            "speed": self.speed,

            "frames_seen": self.frames_seen,

            "status": self.status,

            "threat_score": self.threat_score,

            "threat_level": self.threat_level,

            "distance": self.distance,

            "stationary_frames": self.stationary_frames,

            "is_stationary": self.is_stationary,

            "movement": self.movement_status(),

            "center": self.center,

            "history": self.history,

            "area": self.area(),

            "crossing_events": [
                event.to_dict()
                for event in self.crossing_events
            ],

        }