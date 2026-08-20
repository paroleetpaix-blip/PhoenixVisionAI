"""
========================================================
PHOENIX VISION AI

Intelligence Center

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from threading import RLock

from core.intelligence.alert import Alert


class IntelligenceCenter:

    def __init__(
        self,
        max_alerts=1000
    ):

        self.alerts = []

        self.max_alerts = max(
            100,
            int(max_alerts)
        )

        self._active_by_vehicle = {}

        self._active_watchlist = {}

        self._lock = RLock()


    @staticmethod
    def _message_for_vehicle(
        vehicle,
        level
    ):

        status = str(
            getattr(
                vehicle,
                "status",
                ""
            )
        ).upper()


        if (
            level == "CRITICAL"
            and
            status == "WANTED"
        ):

            return (
                "Véhicule recherché détecté "
                "— intervention immédiate"
            )


        if level == "CRITICAL":

            return (
                "Niveau de menace critique "
                "— intervention immédiate"
            )


        return (
            "Véhicule à surveiller "
            "— niveau de menace élevé"
        )


    def _trim(
        self
    ):

        overflow = (
            len(self.alerts)
            -
            self.max_alerts
        )

        if overflow <= 0:

            return


        removable = []

        for alert in self.alerts:

            if (
                alert.status == "RESOLVED"
                and
                len(removable) < overflow
            ):

                removable.append(
                    alert
                )


        for alert in removable:

            self.alerts.remove(
                alert
            )


        overflow = (
            len(self.alerts)
            -
            self.max_alerts
        )


        if overflow > 0:

            self.alerts = self.alerts[
                overflow:
            ]


    def analyze_vehicle(
        self,
        vehicle
    ):

        vehicle_uuid = getattr(
            vehicle,
            "uuid",
            None
        )

        if not vehicle_uuid:

            return None


        level = str(
            getattr(
                vehicle,
                "threat_level",
                "LOW"
            )
        ).upper()


        threat_score = int(
            getattr(
                vehicle,
                "threat_score",
                0
            )
            or 0
        )


        tracker_id = getattr(
            vehicle,
            "tracker_id",
            None
        )


        with self._lock:

            existing = (
                self._active_by_vehicle.get(
                    vehicle_uuid
                )
            )


            # LOW / MEDIUM ne génèrent pas
            # d'alerte opérateur.
            if level not in {
                "HIGH",
                "CRITICAL"
            }:

                if existing:

                    existing.resolve()

                    self._active_by_vehicle.pop(
                        vehicle_uuid,
                        None
                    )

                return None


            # Même alerte déjà ouverte :
            # mise à jour uniquement.
            if (
                existing
                and
                existing.level == level
                and
                existing.status
                in {
                    "ACTIVE",
                    "ACKNOWLEDGED"
                }
            ):

                existing.touch(
                    threat_score
                )

                return None


            # Escalade HIGH -> CRITICAL :
            # clôturer l'ancienne et créer
            # une nouvelle alerte traçable.
            if existing:

                existing.resolve()

                self._active_by_vehicle.pop(
                    vehicle_uuid,
                    None
                )


            alert = Alert(

                vehicle_uuid=vehicle_uuid,

                tracker_id=tracker_id,

                level=level,

                threat_score=threat_score,

                alert_type="VEHICLE_THREAT",

                message=self._message_for_vehicle(
                    vehicle,
                    level
                )

            )


            self.alerts.append(
                alert
            )

            self._active_by_vehicle[
                vehicle_uuid
            ] = alert


            self._trim()


            return alert


    def create_watchlist_match(
        self,
        vehicle,
        entry,
        plate_confidence=0.0
    ):

        if not isinstance(
            entry,
            dict
        ):

            return None


        vehicle_uuid = getattr(
            vehicle,
            "uuid",
            None
        )


        entry_uuid = entry.get(
            "uuid"
        )


        plate = entry.get(
            "plate"
        )


        if (
            not vehicle_uuid
            or
            not entry_uuid
            or
            not plate
        ):

            return None


        key = (
            str(vehicle_uuid),
            str(entry_uuid)
        )


        priority = str(
            entry.get(
                "priority"
            )
            or
            "MEDIUM"
        ).upper()


        level = (
            "CRITICAL"
            if priority == "CRITICAL"
            else
            "HIGH"
        )


        category = str(
            entry.get(
                "category"
            )
            or
            "WATCHLIST"
        ).upper()


        category_labels = {

            "STOLEN":
                "VÉHICULE VOLÉ",

            "WANTED":
                "VÉHICULE RECHERCHÉ",

            "SUSPICIOUS":
                "VÉHICULE À SURVEILLER",

            "SECURITY":
                "SIGNALEMENT DE SÉCURITÉ",

            "WATCHLIST":
                "LISTE DE SURVEILLANCE",

        }


        category_label = (
            category_labels.get(
                category,
                category
            )
        )


        try:

            plate_confidence = float(
                plate_confidence
                or 0.0
            )

        except (
            TypeError,
            ValueError
        ):

            plate_confidence = 0.0


        tracker_id = getattr(
            vehicle,
            "tracker_id",
            None
        )


        threat_score = int(
            getattr(
                vehicle,
                "threat_score",
                0
            )
            or 0
        )


        with self._lock:

            existing = (
                self._active_watchlist.get(
                    key
                )
            )


            if (
                existing is not None

                and

                existing.status
                in {
                    "ACTIVE",
                    "ACKNOWLEDGED"
                }
            ):

                existing.touch()


                previous = (
                    existing.metadata.get(
                        "plate_confidence",
                        0.0
                    )
                )


                try:

                    previous = float(
                        previous
                        or 0.0
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    previous = 0.0


                if (
                    plate_confidence
                    >
                    previous
                ):

                    existing.metadata[
                        "plate_confidence"
                    ] = round(
                        plate_confidence,
                        1
                    )


                return None


            message = (

                "Correspondance liste de surveillance "
                f"— {plate} "
                f"— {category_label}"

            )


            alert = Alert(

                vehicle_uuid=
                    vehicle_uuid,

                tracker_id=
                    tracker_id,

                level=
                    level,

                threat_score=
                    threat_score,

                alert_type=
                    "WATCHLIST_MATCH",

                message=
                    message,

                metadata={

                    "watchlist_entry_uuid":
                        entry_uuid,

                    "plate":
                        plate,

                    "category":
                        category,

                    "category_label":
                        category_label,

                    "priority":
                        priority,

                    "plate_confidence":
                        round(
                            plate_confidence,
                            1
                        ),

                }

            )


            self.alerts.append(
                alert
            )


            self._active_watchlist[
                key
            ] = alert


            self._trim()


            return alert


    def total_alerts(
        self
    ):

        with self._lock:

            return len(
                self.alerts
            )


    def get_alerts(
        self
    ):

        with self._lock:

            return list(
                self.alerts
            )


    def recent(
        self,
        limit=250
    ):

        limit = max(
            1,
            min(
                int(limit),
                1000
            )
        )


        with self._lock:

            return list(
                reversed(
                    self.alerts[
                        -limit:
                    ]
                )
            )


    def get(
        self,
        alert_uuid
    ):

        with self._lock:

            for alert in self.alerts:

                if (
                    alert.uuid
                    ==
                    alert_uuid
                ):

                    return alert


        return None


    def acknowledge(
        self,
        alert_uuid
    ):

        alert = self.get(
            alert_uuid
        )


        if alert is None:

            return None


        alert.acknowledge()


        return alert


    def stats(
        self
    ):

        with self._lock:

            open_alerts = [

                alert

                for alert in self.alerts

                if alert.status
                in {
                    "ACTIVE",
                    "ACKNOWLEDGED"
                }

            ]


            return {

                "total":
                    len(
                        self.alerts
                    ),

                "open":
                    len(
                        open_alerts
                    ),

                "high":
                    sum(
                        1
                        for alert in open_alerts
                        if alert.level == "HIGH"
                    ),

                "critical":
                    sum(
                        1
                        for alert in open_alerts
                        if alert.level == "CRITICAL"
                    ),

                "acknowledged":
                    sum(
                        1
                        for alert in open_alerts
                        if alert.status == "ACKNOWLEDGED"
                    )

            }


intelligence_center = (
    IntelligenceCenter()
)
