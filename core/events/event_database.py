"""
========================================================
PHOENIX VISION AI ENTERPRISE

Persistent Event Database

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
from pathlib import Path
from threading import RLock

import sqlite3


class EventDatabase:

    def __init__(
        self,
        database_path="data/events.db"
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

        self.connection.row_factory = sqlite3.Row

        self.create_tables()


    def create_tables(
        self
    ):

        with self.lock:

            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events(

                    uuid TEXT PRIMARY KEY,

                    event_type TEXT
                    NOT NULL,

                    vehicle_uuid TEXT,

                    tracker_id INTEGER,

                    description TEXT,

                    timestamp TEXT
                    NOT NULL,

                    level TEXT
                    NOT NULL,

                    persisted_at TEXT
                    NOT NULL

                )
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_timestamp
                ON events(timestamp)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_type
                ON events(event_type)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_level
                ON events(level)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_vehicle
                ON events(vehicle_uuid)
                """
            )


            self.connection.commit()


    @staticmethod
    def _iso(
        value
    ):

        if isinstance(
            value,
            datetime
        ):

            return value.isoformat()


        if value is None:

            return None


        return str(
            value
        )


    @staticmethod
    def _normalize_bound(
        value
    ):

        if value is None:

            return None


        if isinstance(
            value,
            datetime
        ):

            return value.isoformat()


        return str(
            value
        )


    def save(
        self,
        event
    ):

        if event is None:

            return False


        event_uuid = getattr(
            event,
            "uuid",
            None
        )


        if not event_uuid:

            return False


        timestamp = self._iso(
            getattr(
                event,
                "timestamp",
                None
            )
        )


        if not timestamp:

            return False


        with self.lock:

            self.connection.execute(
                """
                INSERT INTO events(

                    uuid,
                    event_type,
                    vehicle_uuid,
                    tracker_id,
                    description,
                    timestamp,
                    level,
                    persisted_at

                )

                VALUES(
                    ?,?,?,?,?,?,?,?
                )

                ON CONFLICT(uuid)
                DO UPDATE SET

                    event_type =
                        excluded.event_type,

                    vehicle_uuid =
                        excluded.vehicle_uuid,

                    tracker_id =
                        excluded.tracker_id,

                    description =
                        excluded.description,

                    timestamp =
                        excluded.timestamp,

                    level =
                        excluded.level
                """,
                (
                    str(
                        event_uuid
                    ),

                    str(
                        getattr(
                            event,
                            "type",
                            "UNKNOWN"
                        )
                    ),

                    getattr(
                        event,
                        "vehicle_uuid",
                        None
                    ),

                    getattr(
                        event,
                        "tracker_id",
                        None
                    ),

                    str(
                        getattr(
                            event,
                            "description",
                            ""
                        )
                    ),

                    timestamp,

                    str(
                        getattr(
                            event,
                            "level",
                            "INFO"
                        )
                    ).upper(),

                    datetime.now()
                    .isoformat()
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
                FROM events
                """
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    def between(
        self,
        start,
        end,
        limit=1000
    ):

        start = self._normalize_bound(
            start
        )

        end = self._normalize_bound(
            end
        )


        if not start or not end:

            raise ValueError(
                "start et end sont obligatoires."
            )


        limit = max(
            1,
            min(
                int(limit),
                10000
            )
        )


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *

                FROM events

                WHERE timestamp >= ?
                  AND timestamp <= ?

                ORDER BY timestamp DESC

                LIMIT ?
                """,
                (
                    start,
                    end,
                    limit
                )
            ).fetchall()


        return [
            self.row_to_dict(
                row
            )
            for row in rows
        ]


    def stats_between(
        self,
        start,
        end
    ):

        start = self._normalize_bound(
            start
        )

        end = self._normalize_bound(
            end
        )


        with self.lock:

            row = self.connection.execute(
                """
                SELECT

                    COUNT(*) AS total,

                    SUM(
                        CASE
                            WHEN level IN (
                                'WARNING',
                                'DANGER'
                            )
                            THEN 1
                            ELSE 0
                        END
                    ) AS warnings,

                    SUM(
                        CASE
                            WHEN level = 'CRITICAL'
                            THEN 1
                            ELSE 0
                        END
                    ) AS critical

                FROM events

                WHERE timestamp >= ?
                  AND timestamp <= ?
                """,
                (
                    start,
                    end
                )
            ).fetchone()


        return {

            "total":
                int(
                    row["total"]
                    or 0
                ),

            "warnings":
                int(
                    row["warnings"]
                    or 0
                ),

            "critical":
                int(
                    row["critical"]
                    or 0
                )

        }


    def stats(
        self
    ):

        today = (
            datetime.now()
            .date()
            .isoformat()
        )


        with self.lock:

            row = self.connection.execute(
                """
                SELECT

                    COUNT(*) AS total,

                    SUM(
                        CASE
                            WHEN substr(
                                timestamp,
                                1,
                                10
                            ) = ?
                            THEN 1
                            ELSE 0
                        END
                    ) AS today,

                    SUM(
                        CASE
                            WHEN level IN (
                                'WARNING',
                                'DANGER'
                            )
                            THEN 1
                            ELSE 0
                        END
                    ) AS warnings,

                    SUM(
                        CASE
                            WHEN level = 'CRITICAL'
                            THEN 1
                            ELSE 0
                        END
                    ) AS critical

                FROM events
                """,
                (
                    today,
                )
            ).fetchone()


        return {

            "total":
                int(
                    row["total"]
                    or 0
                ),

            "today":
                int(
                    row["today"]
                    or 0
                ),

            "warnings":
                int(
                    row["warnings"]
                    or 0
                ),

            "critical":
                int(
                    row["critical"]
                    or 0
                )

        }


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

                FROM events

                ORDER BY timestamp DESC

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


    @staticmethod
    def row_to_dict(
        row
    ):

        data = dict(
            row
        )


        data["type"] = data.pop(
            "event_type",
            "UNKNOWN"
        )


        return data


event_database = EventDatabase()
