"""
========================================================
PHOENIX VISION AI

Vehicle History Database

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from datetime import date
from pathlib import Path
from threading import RLock

import json
import math
import sqlite3


class HistoryDatabase:

    COLUMNS = (
        "uuid",
        "tracker_id",
        "label",
        "plate",
        "plate_raw",
        "plate_confidence",
        "plate_status",
        "plate_last_seen",
        "color",
        "brand",
        "model",
        "first_seen",
        "last_seen",
        "total_frames",
        "max_speed",
        "direction",
        "zone",
        "threat_level",
        "threat_score",
        "status",
        "alerts",
        "crossings",
        "created_at",
        "last_camera",
        "cameras_seen",
        "zones_history",
        "trajectory",
    )


    def __init__(
        self,
        database_path="database/vehicle_history.db"
    ):

        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.lock = RLock()

        self.connection = sqlite3.connect(
            str(self.database_path),
            check_same_thread=False
        )

        self.connection.row_factory = (
            sqlite3.Row
        )

        self.cursor = (
            self.connection.cursor()
        )

        self.create_tables()


    def create_tables(
        self
    ):

        with self.lock:

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vehicle_history(

                    uuid TEXT PRIMARY KEY,
                    tracker_id INTEGER,
                    label TEXT,
                    plate TEXT,
                    plate_raw TEXT,
                    plate_confidence REAL DEFAULT 0,
                    plate_status TEXT,
                    plate_last_seen TEXT,
                    color TEXT,
                    brand TEXT,
                    model TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    total_frames INTEGER,
                    max_speed REAL,
                    direction TEXT,
                    zone TEXT,
                    threat_level TEXT,
                    threat_score INTEGER,
                    status TEXT,
                    alerts INTEGER,
                    crossings INTEGER,
                    created_at TEXT,
                    last_camera TEXT,
                    cameras_seen TEXT,
                    zones_history TEXT,
                    trajectory TEXT

                )
                """
            )

            self.connection.commit()


        self.migrate_schema()

        self.create_anpr_indexes()


    def migrate_schema(
        self
    ):

        required_columns = {

            "uuid": "TEXT",
            "tracker_id": "INTEGER",
            "label": "TEXT",
            "plate": "TEXT",
            "plate_raw": "TEXT",
            "plate_confidence": "REAL DEFAULT 0",
            "plate_status": "TEXT",
            "plate_last_seen": "TEXT",
            "color": "TEXT",
            "brand": "TEXT",
            "model": "TEXT",
            "first_seen": "TEXT",
            "last_seen": "TEXT",
            "total_frames": "INTEGER DEFAULT 0",
            "max_speed": "REAL DEFAULT 0",
            "direction": "TEXT",
            "zone": "TEXT",
            "threat_level": "TEXT",
            "threat_score": "INTEGER DEFAULT 0",
            "status": "TEXT",
            "alerts": "INTEGER DEFAULT 0",
            "crossings": "INTEGER DEFAULT 0",
            "created_at": "TEXT",

            "last_camera": "TEXT",
            "cameras_seen": "TEXT",
            "zones_history": "TEXT",
            "trajectory": "TEXT",
        }


        with self.lock:

            rows = self.connection.execute(
                """
                PRAGMA table_info(
                    vehicle_history
                )
                """
            ).fetchall()


            existing_columns = {
                row["name"]
                for row in rows
            }


            added_columns = []


            for (
                column_name,
                column_type
            ) in required_columns.items():

                if (
                    column_name
                    in existing_columns
                ):

                    continue


                self.connection.execute(
                    f"""
                    ALTER TABLE vehicle_history
                    ADD COLUMN {column_name}
                    {column_type}
                    """
                )


                added_columns.append(
                    column_name
                )


            if (
                "created_at"
                in added_columns
            ):

                self.connection.execute(
                    """
                    UPDATE vehicle_history

                    SET created_at =
                        COALESCE(
                            first_seen,
                            last_seen
                        )

                    WHERE created_at IS NULL
                       OR TRIM(created_at) = ''
                    """
                )


            self.connection.commit()


        if added_columns:

            print(
                "[HISTORY] Migration SQLite :",
                ", ".join(
                    added_columns
                )
            )


    @staticmethod
    def _compact_sequence(
        values
    ):

        compact = []


        for value in values or []:

            if value is None:

                continue


            value = str(
                value
            ).strip()


            if not value:

                continue


            if (
                compact
                and
                compact[-1] == value
            ):

                continue


            compact.append(
                value
            )


        return compact


    @staticmethod
    def _trajectory(
        positions,
        max_points=120
    ):

        valid = []


        for position in positions or []:

            if (
                not isinstance(
                    position,
                    (
                        tuple,
                        list
                    )
                )
                or
                len(position) < 2
            ):

                continue


            try:

                x = float(
                    position[0]
                )

                y = float(
                    position[1]
                )

            except (
                TypeError,
                ValueError
            ):

                continue


            if (
                not math.isfinite(x)
                or
                not math.isfinite(y)
            ):

                continue


            valid.append(
                [
                    round(x, 2),
                    round(y, 2)
                ]
            )


        if (
            len(valid)
            <=
            max_points
        ):

            return valid


        step = max(
            1,
            math.ceil(
                len(valid)
                /
                max_points
            )
        )


        sampled = valid[
            ::step
        ]


        if (
            sampled
            and
            sampled[-1]
            !=
            valid[-1]
        ):

            sampled.append(
                valid[-1]
            )


        return sampled


    @staticmethod
    def should_persist_source(
        source
    ):

        """
        Les fichiers vidéo locaux sont considérés
        comme sources de développement / test.

        Ils peuvent être analysés par Phoenix,
        mais ne doivent pas alimenter l'historique
        opérationnel persistant.
        """

        if source is None:

            return True


        if isinstance(
            source,
            int
        ):

            return True


        source_text = str(
            source
        ).strip()


        if not source_text:

            return True


        # Index caméra transmis sous forme de texte.
        if source_text.isdigit():

            return True


        # RTSP / HTTP / HTTPS = source réseau.
        if "://" in source_text:

            return True


        try:

            source_path = Path(
                source_text
            )

            if source_path.is_file():

                return False

        except OSError:

            pass


        return True


    def create_anpr_indexes(
        self
    ):

        """
        Index utilisés par les recherches LAPI.
        """

        with self.lock:

            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_vehicle_history_plate
                ON vehicle_history(plate)
                """
            )

            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_vehicle_history_plate_status
                ON vehicle_history(plate_status)
                """
            )

            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_vehicle_history_plate_last_seen
                ON vehicle_history(plate_last_seen)
                """
            )

            self.connection.commit()


    def save_vehicle(
        self,
        vehicle,
        memory,
        source=None
    ):

        if (
            vehicle is None
            or
            memory is None
        ):

            return False


        if not self.should_persist_source(
            source
        ):

            return False


        cameras_seen = list(
            getattr(
                memory,
                "cameras_seen",
                []
            )
            or
            []
        )


        zones_history = (
            self._compact_sequence(
                getattr(
                    memory,
                    "zone_history",
                    []
                )
            )
        )


        trajectory = (
            self._trajectory(
                getattr(
                    memory,
                    "positions",
                    []
                )
            )
        )


        with self.lock:

            self.cursor.execute(
                """
                INSERT OR REPLACE INTO vehicle_history(

                    uuid,
                    tracker_id,
                    label,
                    plate,
                    plate_raw,
                    plate_confidence,
                    plate_status,
                    plate_last_seen,
                    color,
                    brand,
                    model,
                    first_seen,
                    last_seen,
                    total_frames,
                    max_speed,
                    direction,
                    zone,
                    threat_level,
                    threat_score,
                    status,
                    alerts,
                    crossings,
                    created_at,
                    last_camera,
                    cameras_seen,
                    zones_history,
                    trajectory

                )

                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?
                )
                """,

                (

                    vehicle.uuid,
                    vehicle.tracker_id,
                    vehicle.label,
                    vehicle.plate,

                    getattr(
                        vehicle,
                        "plate_raw",
                        None
                    ),

                    getattr(
                        vehicle,
                        "plate_confidence",
                        0.0
                    ),

                    getattr(
                        vehicle,
                        "plate_status",
                        None
                    ),

                    (
                        str(
                            getattr(
                                vehicle,
                                "plate_last_seen"
                            )
                        )
                        if getattr(
                            vehicle,
                            "plate_last_seen",
                            None
                        ) is not None
                        else None
                    ),

                    vehicle.color,
                    vehicle.brand,
                    vehicle.model,

                    str(
                        memory.first_seen
                    ),

                    str(
                        memory.last_seen
                    ),

                    memory.total_frames,
                    memory.max_speed,
                    vehicle.direction,
                    vehicle.zone,
                    vehicle.threat_level,
                    vehicle.threat_score,
                    vehicle.status,

                    len(
                        memory.alerts
                    ),

                    len(
                        vehicle.crossing_events
                    ),

                    str(
                        memory.first_seen
                    ),

                    getattr(
                        memory,
                        "last_camera",
                        None
                    ),

                    json.dumps(
                        cameras_seen,
                        ensure_ascii=False
                    ),

                    json.dumps(
                        zones_history,
                        ensure_ascii=False
                    ),

                    json.dumps(
                        trajectory,
                        ensure_ascii=False
                    ),

                )
            )

            self.connection.commit()


        return True


    def total(
        self
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM vehicle_history
                """
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    def today_total(
        self
    ):

        today = (
            date.today()
            .isoformat()
        )


        with self.lock:

            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM vehicle_history
                WHERE substr(created_at, 1, 10) = ?
                """,
                (
                    today,
                )
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    def plates_total(
        self
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM vehicle_history
                WHERE plate IS NOT NULL
                  AND TRIM(plate) != ''
                """
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    def anpr_stats(
        self
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT

                    SUM(
                        CASE
                            WHEN plate IS NOT NULL
                             AND TRIM(plate) != ''
                            THEN 1
                            ELSE 0
                        END
                    ) AS plates_detected,

                    SUM(
                        CASE
                            WHEN UPPER(
                                COALESCE(
                                    plate_status,
                                    ''
                                )
                            ) = 'VALIDATED'
                            THEN 1
                            ELSE 0
                        END
                    ) AS validated,

                    SUM(
                        CASE
                            WHEN UPPER(
                                COALESCE(
                                    plate_status,
                                    ''
                                )
                            )
                            IN (
                                'LOW_CONFIDENCE',
                                'INVALID_TEXT'
                            )
                            THEN 1
                            ELSE 0
                        END
                    ) AS to_review,

                    AVG(
                        CASE
                            WHEN COALESCE(
                                plate_confidence,
                                0
                            ) > 0
                            THEN plate_confidence
                            ELSE NULL
                        END
                    ) AS average_confidence

                FROM vehicle_history
                """
            ).fetchone()


        return {

            "plates_detected":
                int(
                    row["plates_detected"]
                    or 0
                ),

            "validated":
                int(
                    row["validated"]
                    or 0
                ),

            "to_review":
                int(
                    row["to_review"]
                    or 0
                ),

            "average_confidence":
                round(
                    float(
                        row["average_confidence"]
                        or 0.0
                    ),
                    1
                )

        }


    def threats_total(
        self
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT COUNT(*)
                FROM vehicle_history
                WHERE UPPER(
                    COALESCE(
                        threat_level,
                        ''
                    )
                )
                IN (
                    'HIGH',
                    'CRITICAL'
                )
                """
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    @staticmethod
    def _json_value(
        value,
        fallback
    ):

        if (
            value is None
            or
            value == ""
        ):

            return fallback


        try:

            return json.loads(
                value
            )

        except (
            TypeError,
            json.JSONDecodeError
        ):

            return fallback


    @classmethod
    def row_to_dict(
        cls,
        row
    ):

        if row is None:

            return None


        record = {}


        row_keys = set(
            row.keys()
        )


        for column in cls.COLUMNS:

            record[column] = (
                row[column]
                if column in row_keys
                else None
            )


        record["cameras_seen"] = (
            cls._json_value(
                record["cameras_seen"],
                []
            )
        )


        record["zones_history"] = (
            cls._json_value(
                record["zones_history"],
                []
            )
        )


        record["trajectory"] = (
            cls._json_value(
                record["trajectory"],
                []
            )
        )


        return record


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


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                ORDER BY
                    COALESCE(
                        last_seen,
                        created_at
                    )
                DESC
                LIMIT ?
                """,
                (
                    limit,
                )
            ).fetchall()


        return [
            self.row_to_dict(
                row
            )
            for row in rows
        ]


    def anpr_recent(
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


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *
                FROM vehicle_history

                WHERE

                    (
                        plate IS NOT NULL
                        AND
                        TRIM(plate) != ''
                    )

                    OR

                    (
                        plate_raw IS NOT NULL
                        AND
                        TRIM(plate_raw) != ''
                    )

                    OR

                    (
                        plate_status IS NOT NULL
                        AND
                        TRIM(plate_status) != ''
                        AND
                        UPPER(plate_status)
                        !=
                        'NOT_DETECTED'
                    )

                ORDER BY

                    COALESCE(
                        plate_last_seen,
                        last_seen,
                        created_at
                    )

                DESC

                LIMIT ?
                """,
                (
                    limit,
                )
            ).fetchall()


        return [

            self.row_to_dict(
                row
            )

            for row in rows

        ]


    def find_by_uuid(
        self,
        uuid
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE uuid=?
                """,
                (
                    uuid,
                )
            ).fetchone()


    def plate_forensic(
        self,
        plate,
        limit=1000
    ):

        normalized_plate = str(
            plate or ""
        ).strip().upper()


        if not normalized_plate:

            return {

                "plate":
                    None,

                "occurrences":
                    0,

                "first_detection":
                    None,

                "last_detection":
                    None,

                "max_confidence":
                    0.0,

                "validated":
                    0,

                "to_review":
                    0,

                "cameras":
                    [],

                "zones":
                    [],

                "records":
                    []

            }


        limit = max(
            1,
            min(
                int(limit),
                5000
            )
        )


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *
                FROM vehicle_history

                WHERE UPPER(
                    TRIM(
                        COALESCE(
                            plate,
                            ''
                        )
                    )
                ) = ?

                ORDER BY

                    COALESCE(
                        plate_last_seen,
                        last_seen,
                        created_at
                    )

                DESC

                LIMIT ?
                """,
                (
                    normalized_plate,
                    limit
                )
            ).fetchall()


        records = [

            self.row_to_dict(
                row
            )

            for row in rows

        ]


        if not records:

            return {

                "plate":
                    normalized_plate,

                "occurrences":
                    0,

                "first_detection":
                    None,

                "last_detection":
                    None,

                "max_confidence":
                    0.0,

                "validated":
                    0,

                "to_review":
                    0,

                "cameras":
                    [],

                "zones":
                    [],

                "records":
                    []

            }


        first_candidates = [

            str(
                record.get(
                    "first_seen"
                )
            )

            for record in records

            if record.get(
                "first_seen"
            )

        ]


        last_candidates = [

            str(
                record.get(
                    "plate_last_seen"
                )
                or
                record.get(
                    "last_seen"
                )
                or
                record.get(
                    "created_at"
                )
            )

            for record in records

            if (
                record.get(
                    "plate_last_seen"
                )
                or
                record.get(
                    "last_seen"
                )
                or
                record.get(
                    "created_at"
                )
            )

        ]


        confidences = []


        for record in records:

            try:

                value = float(
                    record.get(
                        "plate_confidence"
                    )
                    or 0
                )

            except (
                TypeError,
                ValueError
            ):

                value = 0.0


            if value > 0:

                confidences.append(
                    value
                )


        cameras = []

        zones = []


        def append_unique(
            target,
            value
        ):

            if (
                value is None
                or
                str(value).strip() == ""
            ):

                return


            value = str(
                value
            )


            if value not in target:

                target.append(
                    value
                )


        validated = 0

        to_review = 0


        for record in records:

            append_unique(
                cameras,
                record.get(
                    "last_camera"
                )
            )


            for camera in (
                record.get(
                    "cameras_seen"
                )
                or
                []
            ):

                append_unique(
                    cameras,
                    camera
                )


            append_unique(
                zones,
                record.get(
                    "zone"
                )
            )


            for zone in (
                record.get(
                    "zones_history"
                )
                or
                []
            ):

                append_unique(
                    zones,
                    zone
                )


            status = str(
                record.get(
                    "plate_status"
                )
                or ""
            ).upper()


            if status == "VALIDATED":

                validated += 1


            if status in {
                "LOW_CONFIDENCE",
                "INVALID_TEXT"
            }:

                to_review += 1


        return {

            "plate":
                normalized_plate,

            "occurrences":
                len(
                    records
                ),

            "first_detection":
                (
                    min(
                        first_candidates
                    )
                    if first_candidates
                    else None
                ),

            "last_detection":
                (
                    max(
                        last_candidates
                    )
                    if last_candidates
                    else None
                ),

            "max_confidence":
                round(
                    max(
                        confidences
                    )
                    if confidences
                    else 0.0,
                    1
                ),

            "validated":
                validated,

            "to_review":
                to_review,

            "cameras":
                cameras,

            "zones":
                zones,

            "records":
                records

        }


    def find_by_plate(
        self,
        plate
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE plate=?
                """,
                (
                    plate,
                )
            ).fetchall()


    def find_by_color(
        self,
        color
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE color=?
                """,
                (
                    color,
                )
            ).fetchall()


    def find_by_brand(
        self,
        brand
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE brand=?
                """,
                (
                    brand,
                )
            ).fetchall()


    def find_by_model(
        self,
        model
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE model=?
                """,
                (
                    model,
                )
            ).fetchall()


    def find_by_threat(
        self,
        threat
    ):

        with self.lock:

            return self.connection.execute(
                """
                SELECT *
                FROM vehicle_history
                WHERE threat_level=?
                """,
                (
                    threat,
                )
            ).fetchall()


    def stats(
        self
    ):

        return {
            "total":
                self.total(),

            "today":
                self.today_total(),

            "plates":
                self.plates_total(),

            "threats":
                self.threats_total()
        }


history_database = (
    HistoryDatabase()
)
