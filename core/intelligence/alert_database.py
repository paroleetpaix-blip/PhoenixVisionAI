"""
========================================================
PHOENIX VISION AI ENTERPRISE

Persistent Intelligence Alert Database

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
from pathlib import Path
from threading import RLock

import json
import sqlite3


class AlertDatabase:

    def __init__(
        self,
        database_path="data/alerts.db"
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
                CREATE TABLE IF NOT EXISTS alerts(

                    uuid TEXT PRIMARY KEY,

                    alert_type TEXT
                    NOT NULL,

                    vehicle_uuid TEXT,

                    tracker_id INTEGER,

                    metadata_json TEXT
                    NOT NULL,

                    level TEXT
                    NOT NULL,

                    message TEXT,

                    threat_score INTEGER
                    NOT NULL
                    DEFAULT 0,

                    status TEXT
                    NOT NULL,

                    timestamp TEXT
                    NOT NULL,

                    last_seen TEXT
                    NOT NULL,

                    acknowledged_at TEXT,

                    resolved_at TEXT,

                    persisted_at TEXT
                    NOT NULL,

                    updated_at TEXT
                    NOT NULL

                )
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_timestamp
                ON alerts(timestamp)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_last_seen
                ON alerts(last_seen)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_status
                ON alerts(status)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_level
                ON alerts(level)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_type
                ON alerts(alert_type)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_alerts_vehicle
                ON alerts(vehicle_uuid)
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
    def _json(
        value
    ):

        if not isinstance(
            value,
            dict
        ):

            value = {}


        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            default=str
        )


    @staticmethod
    def _normalize_bound(
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


    def save(
        self,
        alert
    ):

        if alert is None:

            return False


        alert_uuid = getattr(
            alert,
            "uuid",
            None
        )


        if not alert_uuid:

            return False


        timestamp = self._iso(
            getattr(
                alert,
                "timestamp",
                None
            )
        )


        last_seen = self._iso(
            getattr(
                alert,
                "last_seen",
                None
            )
        )


        if not timestamp:

            return False


        if not last_seen:

            last_seen = timestamp


        now = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            self.connection.execute(
                """
                INSERT INTO alerts(

                    uuid,
                    alert_type,
                    vehicle_uuid,
                    tracker_id,
                    metadata_json,
                    level,
                    message,
                    threat_score,
                    status,
                    timestamp,
                    last_seen,
                    acknowledged_at,
                    resolved_at,
                    persisted_at,
                    updated_at

                )

                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )

                ON CONFLICT(uuid)
                DO UPDATE SET

                    alert_type =
                        excluded.alert_type,

                    vehicle_uuid =
                        excluded.vehicle_uuid,

                    tracker_id =
                        excluded.tracker_id,

                    metadata_json =
                        excluded.metadata_json,

                    level =
                        excluded.level,

                    message =
                        excluded.message,

                    threat_score =
                        excluded.threat_score,

                    status =
                        excluded.status,

                    timestamp =
                        excluded.timestamp,

                    last_seen =
                        excluded.last_seen,

                    acknowledged_at =
                        excluded.acknowledged_at,

                    resolved_at =
                        excluded.resolved_at,

                    updated_at =
                        excluded.updated_at
                """,
                (
                    str(
                        alert_uuid
                    ),

                    str(
                        getattr(
                            alert,
                            "type",
                            "VEHICLE_THREAT"
                        )
                    ),

                    getattr(
                        alert,
                        "vehicle_uuid",
                        None
                    ),

                    getattr(
                        alert,
                        "tracker_id",
                        None
                    ),

                    self._json(
                        getattr(
                            alert,
                            "metadata",
                            {}
                        )
                    ),

                    str(
                        getattr(
                            alert,
                            "level",
                            "INFO"
                        )
                    ).upper(),

                    str(
                        getattr(
                            alert,
                            "message",
                            ""
                        )
                    ),

                    int(
                        getattr(
                            alert,
                            "threat_score",
                            0
                        )
                        or 0
                    ),

                    str(
                        getattr(
                            alert,
                            "status",
                            "ACTIVE"
                        )
                    ).upper(),

                    timestamp,

                    last_seen,

                    self._iso(
                        getattr(
                            alert,
                            "acknowledged_at",
                            None
                        )
                    ),

                    self._iso(
                        getattr(
                            alert,
                            "resolved_at",
                            None
                        )
                    ),

                    now,
                    now
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
                FROM alerts
                """
            ).fetchone()


        return int(
            row[0]
            if row
            else 0
        )


    def get(
        self,
        alert_uuid
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT *

                FROM alerts

                WHERE uuid=?

                LIMIT 1
                """,
                (
                    str(
                        alert_uuid
                    ),
                )
            ).fetchone()


        return (
            self.row_to_dict(
                row
            )
            if row
            else None
        )


    def acknowledge(
        self,
        alert_uuid
    ):

        alert_uuid = str(
            alert_uuid
        )


        with self.lock:

            row = self.connection.execute(
                """
                SELECT status

                FROM alerts

                WHERE uuid=?

                LIMIT 1
                """,
                (
                    alert_uuid,
                )
            ).fetchone()


            if row is None:

                return None


            if str(
                row["status"]
            ).upper() != "RESOLVED":

                now = (
                    datetime.now()
                    .isoformat()
                )


                self.connection.execute(
                    """
                    UPDATE alerts

                    SET
                        status='ACKNOWLEDGED',
                        acknowledged_at=?,
                        updated_at=?

                    WHERE uuid=?
                    """,
                    (
                        now,
                        now,
                        alert_uuid
                    )
                )


                self.connection.commit()


            row = self.connection.execute(
                """
                SELECT *

                FROM alerts

                WHERE uuid=?

                LIMIT 1
                """,
                (
                    alert_uuid,
                )
            ).fetchone()


        return (
            self.row_to_dict(
                row
            )
            if row
            else None
        )


    def stats(
        self
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT

                    COUNT(*) AS total,

                    SUM(
                        CASE
                            WHEN status IN (
                                'ACTIVE',
                                'ACKNOWLEDGED'
                            )
                            THEN 1
                            ELSE 0
                        END
                    ) AS open,

                    SUM(
                        CASE
                            WHEN status IN (
                                'ACTIVE',
                                'ACKNOWLEDGED'
                            )
                             AND level = 'HIGH'
                            THEN 1
                            ELSE 0
                        END
                    ) AS high,

                    SUM(
                        CASE
                            WHEN status IN (
                                'ACTIVE',
                                'ACKNOWLEDGED'
                            )
                             AND level = 'CRITICAL'
                            THEN 1
                            ELSE 0
                        END
                    ) AS critical,

                    SUM(
                        CASE
                            WHEN status = 'ACKNOWLEDGED'
                            THEN 1
                            ELSE 0
                        END
                    ) AS acknowledged,

                    SUM(
                        CASE
                            WHEN status = 'RESOLVED'
                            THEN 1
                            ELSE 0
                        END
                    ) AS resolved

                FROM alerts
                """
            ).fetchone()


        return {

            "total":
                int(
                    row["total"]
                    or 0
                ),

            "open":
                int(
                    row["open"]
                    or 0
                ),

            "high":
                int(
                    row["high"]
                    or 0
                ),

            "critical":
                int(
                    row["critical"]
                    or 0
                ),

            "acknowledged":
                int(
                    row["acknowledged"]
                    or 0
                ),

            "resolved":
                int(
                    row["resolved"]
                    or 0
                )

        }


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

                FROM alerts

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


        if not start or not end:

            raise ValueError(
                "start et end sont obligatoires."
            )


        if start > end:

            raise ValueError(
                "start doit être antérieur ou égal à end."
            )


        with self.lock:

            created = self.connection.execute(
                """
                SELECT

                    COUNT(*) AS total,

                    SUM(
                        CASE
                            WHEN level = 'HIGH'
                            THEN 1
                            ELSE 0
                        END
                    ) AS high,

                    SUM(
                        CASE
                            WHEN level = 'CRITICAL'
                            THEN 1
                            ELSE 0
                        END
                    ) AS critical

                FROM alerts

                WHERE timestamp >= ?
                  AND timestamp <= ?
                """,
                (
                    start,
                    end
                )
            ).fetchone()


            lifecycle = self.connection.execute(
                """
                SELECT

                    SUM(
                        CASE
                            WHEN acknowledged_at IS NOT NULL
                             AND acknowledged_at >= ?
                             AND acknowledged_at <= ?
                            THEN 1
                            ELSE 0
                        END
                    ) AS acknowledged,

                    SUM(
                        CASE
                            WHEN resolved_at IS NOT NULL
                             AND resolved_at >= ?
                             AND resolved_at <= ?
                            THEN 1
                            ELSE 0
                        END
                    ) AS resolved,

                    SUM(
                        CASE
                            WHEN timestamp <= ?
                             AND (
                                resolved_at IS NULL
                                OR resolved_at > ?
                             )
                            THEN 1
                            ELSE 0
                        END
                    ) AS open_at_end,

                    SUM(
                        CASE
                            WHEN timestamp <= ?
                             AND (
                                resolved_at IS NULL
                                OR resolved_at >= ?
                             )
                            THEN 1
                            ELSE 0
                        END
                    ) AS active_in_period

                FROM alerts
                """,
                (
                    start,
                    end,

                    start,
                    end,

                    end,
                    end,

                    end,
                    start
                )
            ).fetchone()


        return {

            "total":
                int(
                    created["total"]
                    or 0
                ),

            "high":
                int(
                    created["high"]
                    or 0
                ),

            "critical":
                int(
                    created["critical"]
                    or 0
                ),

            "acknowledged":
                int(
                    lifecycle["acknowledged"]
                    or 0
                ),

            "resolved":
                int(
                    lifecycle["resolved"]
                    or 0
                ),

            "open":
                int(
                    lifecycle["open_at_end"]
                    or 0
                ),

            "open_at_end":
                int(
                    lifecycle["open_at_end"]
                    or 0
                ),

            "active_in_period":
                int(
                    lifecycle["active_in_period"]
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

                FROM alerts

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
            "alert_type",
            "VEHICLE_THREAT"
        )


        raw_metadata = data.pop(
            "metadata_json",
            "{}"
        )


        try:

            data["metadata"] = (
                json.loads(
                    raw_metadata
                )
            )

        except Exception:

            data["metadata"] = {}


        return data


alert_database = AlertDatabase()
