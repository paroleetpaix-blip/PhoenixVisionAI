"""
========================================================
PHOENIX VISION AI ENTERPRISE

Enterprise Report Database

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
from pathlib import Path
from threading import RLock

import hashlib
import json
import sqlite3
import uuid


class ReportDatabase:

    def __init__(
        self,
        database_path="data/reports.db"
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

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.create_tables()


    @staticmethod
    def _json(
        value
    ):

        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":"
            ),
            default=str
        )


    @classmethod
    def _hash(
        cls,
        value
    ):

        payload = cls._json(
            value
        ).encode(
            "utf-8"
        )

        return hashlib.sha256(
            payload
        ).hexdigest()


    @staticmethod
    def _now():

        return (
            datetime.now()
            .isoformat()
        )


    @staticmethod
    def generate_reference():

        date_part = (
            datetime.now()
            .strftime(
                "%Y%m%d"
            )
        )

        random_part = (
            uuid.uuid4()
            .hex[:8]
            .upper()
        )

        return (
            f"PHX-RPT-"
            f"{date_part}-"
            f"{random_part}"
        )


    def create_tables(
        self
    ):

        with self.lock:

            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                reports(

                    uuid TEXT PRIMARY KEY,

                    reference TEXT
                    NOT NULL
                    UNIQUE,

                    report_type TEXT
                    NOT NULL,

                    title TEXT
                    NOT NULL,

                    period_start TEXT,

                    period_end TEXT,

                    scope TEXT,

                    filters_json TEXT
                    NOT NULL,

                    sections_json TEXT
                    NOT NULL,

                    snapshot_json TEXT
                    NOT NULL,

                    snapshot_hash TEXT
                    NOT NULL,

                    generated_by TEXT
                    NOT NULL,

                    generated_role TEXT
                    NOT NULL,

                    generated_at TEXT
                    NOT NULL,

                    status TEXT
                    NOT NULL,

                    version INTEGER
                    NOT NULL
                    DEFAULT 1,

                    company TEXT
                    NOT NULL,

                    product TEXT
                    NOT NULL

                )
                """
            )


            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                report_audit(

                    uuid TEXT PRIMARY KEY,

                    report_uuid TEXT
                    NOT NULL,

                    action TEXT
                    NOT NULL,

                    actor TEXT
                    NOT NULL,

                    actor_role TEXT,

                    timestamp TEXT
                    NOT NULL,

                    details_json TEXT
                    NOT NULL,

                    previous_hash TEXT,

                    event_hash TEXT
                    NOT NULL,

                    FOREIGN KEY(
                        report_uuid
                    )
                    REFERENCES reports(uuid)

                )
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_reports_reference
                ON reports(reference)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_reports_generated_at
                ON reports(generated_at)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_reports_type
                ON reports(report_type)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_report_audit_report
                ON report_audit(report_uuid)
                """
            )


            self.connection.commit()


    def _previous_audit_hash_locked(
        self,
        report_uuid
    ):

        row = self.connection.execute(
            """
            SELECT event_hash

            FROM report_audit

            WHERE report_uuid=?

            ORDER BY rowid DESC

            LIMIT 1
            """,
            (
                report_uuid,
            )
        ).fetchone()


        return (
            row["event_hash"]
            if row
            else None
        )


    def _add_audit_locked(
        self,
        report_uuid,
        action,
        actor,
        actor_role=None,
        details=None
    ):

        event_uuid = str(
            uuid.uuid4()
        )

        timestamp = self._now()

        previous_hash = (
            self
            ._previous_audit_hash_locked(
                report_uuid
            )
        )


        details = (
            details
            if isinstance(
                details,
                dict
            )
            else {}
        )


        material = {

            "uuid":
                event_uuid,

            "report_uuid":
                report_uuid,

            "action":
                str(action),

            "actor":
                str(actor),

            "actor_role":
                (
                    str(actor_role)
                    if actor_role
                    else None
                ),

            "timestamp":
                timestamp,

            "details":
                details,

            "previous_hash":
                previous_hash

        }


        event_hash = self._hash(
            material
        )


        self.connection.execute(
            """
            INSERT INTO report_audit(

                uuid,
                report_uuid,
                action,
                actor,
                actor_role,
                timestamp,
                details_json,
                previous_hash,
                event_hash

            )

            VALUES(
                ?,?,?,?,?,?,?,?,?
            )
            """,
            (
                event_uuid,
                report_uuid,
                str(action),
                str(actor),

                (
                    str(actor_role)
                    if actor_role
                    else None
                ),

                timestamp,

                self._json(
                    details
                ),

                previous_hash,
                event_hash
            )
        )


        return event_uuid


    def add_audit(
        self,
        report_uuid,
        action,
        actor,
        actor_role=None,
        details=None
    ):

        with self.lock:

            event_uuid = (
                self._add_audit_locked(

                    report_uuid,
                    action,
                    actor,
                    actor_role,
                    details

                )
            )

            self.connection.commit()


        return event_uuid


    def create_report(
        self,
        report_type,
        title,
        snapshot,
        generated_by,
        generated_role,
        period_start=None,
        period_end=None,
        scope=None,
        filters=None,
        sections=None
    ):

        if not isinstance(
            snapshot,
            dict
        ):

            raise ValueError(
                "Le snapshot du rapport doit être un dictionnaire."
            )


        report_uuid = str(
            uuid.uuid4()
        )

        reference = (
            self.generate_reference()
        )

        generated_at = (
            self._now()
        )

        filters = (
            filters
            if isinstance(
                filters,
                dict
            )
            else {}
        )

        sections = (
            sections
            if isinstance(
                sections,
                list
            )
            else []
        )


        snapshot_hash = (
            self._hash(
                snapshot
            )
        )


        with self.lock:

            self.connection.execute(
                """
                INSERT INTO reports(

                    uuid,
                    reference,
                    report_type,
                    title,
                    period_start,
                    period_end,
                    scope,
                    filters_json,
                    sections_json,
                    snapshot_json,
                    snapshot_hash,
                    generated_by,
                    generated_role,
                    generated_at,
                    status,
                    version,
                    company,
                    product

                )

                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?
                )
                """,
                (
                    report_uuid,
                    reference,

                    str(
                        report_type
                    ).upper(),

                    str(
                        title
                    ),

                    period_start,
                    period_end,
                    scope,

                    self._json(
                        filters
                    ),

                    self._json(
                        sections
                    ),

                    self._json(
                        snapshot
                    ),

                    snapshot_hash,

                    str(
                        generated_by
                    ),

                    str(
                        generated_role
                    ).upper(),

                    generated_at,

                    "FINAL",

                    1,

                    "Phoenix Security Technologies",

                    "Phoenix Vision AI Enterprise"
                )
            )


            self._add_audit_locked(

                report_uuid,

                "GENERATED",

                generated_by,

                generated_role,

                {
                    "reference":
                        reference,

                    "snapshot_hash":
                        snapshot_hash
                }

            )


            self.connection.commit()


        return self.get(
            report_uuid
        )


    def get(
        self,
        report_uuid
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT *

                FROM reports

                WHERE uuid=?
                """,
                (
                    report_uuid,
                )
            ).fetchone()


        return (
            self.row_to_dict(
                row
            )
            if row
            else None
        )


    def find_by_reference(
        self,
        reference
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT *

                FROM reports

                WHERE reference=?
                """,
                (
                    str(
                        reference
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


    def recent(
        self,
        limit=100
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

                FROM reports

                ORDER BY generated_at DESC

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


    def search(
        self,
        reference=None,
        report_type=None,
        generated_by=None,
        status=None,
        scope=None,
        period_start=None,
        period_end=None,
        limit=100
    ):

        limit = max(
            1,
            min(
                int(limit),
                500
            )
        )


        clauses = []

        parameters = []


        if reference:

            clauses.append(
                "UPPER(reference) LIKE ?"
            )

            parameters.append(
                "%"
                +
                str(
                    reference
                ).strip().upper()
                +
                "%"
            )


        if report_type:

            clauses.append(
                "UPPER(report_type) = ?"
            )

            parameters.append(
                str(
                    report_type
                ).strip().upper()
            )


        if generated_by:

            clauses.append(
                "LOWER(generated_by) LIKE ?"
            )

            parameters.append(
                "%"
                +
                str(
                    generated_by
                ).strip().lower()
                +
                "%"
            )


        if status:

            clauses.append(
                "UPPER(status) = ?"
            )

            parameters.append(
                str(
                    status
                ).strip().upper()
            )


        if scope:

            clauses.append(
                "UPPER(COALESCE(scope, '')) = ?"
            )

            parameters.append(
                str(
                    scope
                ).strip().upper()
            )


        # Recherche par chevauchement
        # de la période du rapport.
        if period_start:

            clauses.append(
                """
                COALESCE(
                    period_end,
                    period_start,
                    generated_at
                ) >= ?
                """
            )

            parameters.append(
                str(
                    period_start
                )
            )


        if period_end:

            clauses.append(
                """
                COALESCE(
                    period_start,
                    generated_at
                ) <= ?
                """
            )

            parameters.append(
                str(
                    period_end
                )
            )


        where = ""

        if clauses:

            where = (
                "WHERE "
                +
                " AND ".join(
                    clauses
                )
            )


        query = f"""
            SELECT

                uuid,
                reference,
                report_type,
                title,
                period_start,
                period_end,
                scope,
                generated_by,
                generated_role,
                generated_at,
                status,
                version,
                company,
                product,
                snapshot_hash

            FROM reports

            {where}

            ORDER BY generated_at DESC

            LIMIT ?
        """


        parameters.append(
            limit
        )


        with self.lock:

            rows = (
                self.connection
                .execute(
                    query,
                    tuple(
                        parameters
                    )
                )
                .fetchall()
            )


        return [
            dict(
                row
            )
            for row in rows
        ]


    def audit_for_report(
        self,
        report_uuid
    ):

        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *

                FROM report_audit

                WHERE report_uuid=?

                ORDER BY rowid ASC
                """,
                (
                    report_uuid,
                )
            ).fetchall()


        result = []


        for row in rows:

            data = dict(
                row
            )


            try:

                data[
                    "details"
                ] = json.loads(
                    data.pop(
                        "details_json"
                    )
                )

            except Exception:

                data[
                    "details"
                ] = {}


            result.append(
                data
            )


        return result


    def verify_report_integrity(
        self,
        report_uuid
    ):

        report = self.get(
            report_uuid
        )


        if report is None:

            return {

                "exists":
                    False,

                "snapshot_valid":
                    False,

                "audit_valid":
                    False

            }


        snapshot_valid = (
            self._hash(
                report[
                    "snapshot"
                ]
            )
            ==
            report[
                "snapshot_hash"
            ]
        )


        events = (
            self.audit_for_report(
                report_uuid
            )
        )


        previous_hash = None

        audit_valid = True


        for event in events:

            material = {

                "uuid":
                    event["uuid"],

                "report_uuid":
                    event[
                        "report_uuid"
                    ],

                "action":
                    event[
                        "action"
                    ],

                "actor":
                    event[
                        "actor"
                    ],

                "actor_role":
                    event[
                        "actor_role"
                    ],

                "timestamp":
                    event[
                        "timestamp"
                    ],

                "details":
                    event[
                        "details"
                    ],

                "previous_hash":
                    previous_hash

            }


            expected = (
                self._hash(
                    material
                )
            )


            if (
                event[
                    "previous_hash"
                ]
                !=
                previous_hash
                or
                event[
                    "event_hash"
                ]
                !=
                expected
            ):

                audit_valid = False

                break


            previous_hash = (
                event[
                    "event_hash"
                ]
            )


        return {

            "exists":
                True,

            "snapshot_valid":
                snapshot_valid,

            "audit_valid":
                audit_valid,

            "events":
                len(
                    events
                )

        }


    @staticmethod
    def row_to_dict(
        row
    ):

        data = dict(
            row
        )


        for source, target, fallback in [

            (
                "filters_json",
                "filters",
                {}
            ),

            (
                "sections_json",
                "sections",
                []
            ),

            (
                "snapshot_json",
                "snapshot",
                {}
            ),

        ]:

            raw = data.pop(
                source,
                None
            )


            try:

                data[
                    target
                ] = json.loads(
                    raw
                )

            except Exception:

                data[
                    target
                ] = fallback


        return data


report_database = (
    ReportDatabase()
)
