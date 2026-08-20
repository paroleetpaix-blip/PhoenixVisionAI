"""
========================================================
PHOENIX VISION AI

Liste de surveillance locale

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
from pathlib import Path
from threading import RLock

import sqlite3
import uuid


class WatchlistDatabase:

    def __init__(
        self,
        database_path="data/watchlist.db"
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

        self.create_tables()


    def create_tables(
        self
    ):

        with self.lock:

            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                watchlist_entries(

                    uuid TEXT PRIMARY KEY,

                    plate TEXT NOT NULL,

                    category TEXT NOT NULL,

                    priority TEXT NOT NULL,

                    status TEXT NOT NULL,

                    reason TEXT,

                    case_reference TEXT,

                    authority TEXT,

                    scope TEXT NOT NULL,

                    origin TEXT NOT NULL,

                    external_request_id TEXT,

                    valid_from TEXT,

                    valid_until TEXT,

                    created_by TEXT NOT NULL,

                    approved_by TEXT,

                    created_at TEXT NOT NULL,

                    approved_at TEXT,

                    updated_at TEXT NOT NULL

                )
                """
            )


            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                watchlist_audit(

                    uuid TEXT PRIMARY KEY,

                    entry_uuid TEXT NOT NULL,

                    action TEXT NOT NULL,

                    actor TEXT NOT NULL,

                    actor_role TEXT,

                    timestamp TEXT NOT NULL,

                    details TEXT

                )
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_watchlist_plate
                ON watchlist_entries(plate)
                """
            )


            self.connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_watchlist_status
                ON watchlist_entries(status)
                """
            )


            self.connection.commit()


    @staticmethod
    def normalize_plate(
        value
    ):

        value = str(
            value or ""
        ).upper()

        return "".join(
            character
            for character in value
            if character.isalnum()
        )


    def add_audit(
        self,
        entry_uuid,
        action,
        actor,
        actor_role=None,
        details=None
    ):

        audit_uuid = str(
            uuid.uuid4()
        )

        timestamp = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            self.connection.execute(
                """
                INSERT INTO watchlist_audit(

                    uuid,
                    entry_uuid,
                    action,
                    actor,
                    actor_role,
                    timestamp,
                    details

                )

                VALUES(
                    ?,?,?,?,?,?,?
                )
                """,
                (
                    audit_uuid,
                    entry_uuid,
                    action,
                    actor,
                    actor_role,
                    timestamp,
                    details
                )
            )

            self.connection.commit()


        return audit_uuid


    def propose(
        self,
        plate,
        category,
        priority,
        reason,
        case_reference,
        authority,
        created_by,
        actor_role=None,
        valid_from=None,
        valid_until=None
    ):

        plate = self.normalize_plate(
            plate
        )


        if len(plate) < 3:

            raise ValueError(
                "Plaque invalide."
            )


        entry_uuid = str(
            uuid.uuid4()
        )


        now = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            self.connection.execute(
                """
                INSERT INTO watchlist_entries(

                    uuid,
                    plate,
                    category,
                    priority,
                    status,
                    reason,
                    case_reference,
                    authority,
                    scope,
                    origin,
                    external_request_id,
                    valid_from,
                    valid_until,
                    created_by,
                    approved_by,
                    created_at,
                    approved_at,
                    updated_at

                )

                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?
                )
                """,
                (
                    entry_uuid,
                    plate,
                    category,
                    priority,

                    "PENDING",

                    reason,
                    case_reference,
                    authority,

                    "LOCAL_SITE",
                    "LOCAL_CLIENT",

                    None,

                    valid_from,
                    valid_until,

                    created_by,
                    None,

                    now,
                    None,
                    now
                )
            )

            self.connection.commit()


        self.add_audit(

            entry_uuid,

            "PROPOSED",

            created_by,

            actor_role,

            (
                "Signalement local proposé. "
                f"Catégorie={category}; "
                f"Priorité={priority}"
            )

        )


        return self.find_by_uuid(
            entry_uuid
        )


    def approve(
        self,
        entry_uuid,
        approved_by,
        actor_role=None
    ):

        now = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            cursor = self.connection.execute(
                """
                UPDATE watchlist_entries

                SET
                    status='ACTIVE',
                    approved_by=?,
                    approved_at=?,
                    updated_at=?

                WHERE uuid=?
                  AND status='PENDING'
                """,
                (
                    approved_by,
                    now,
                    now,
                    entry_uuid
                )
            )

            self.connection.commit()


        if cursor.rowcount == 0:

            return None


        self.add_audit(

            entry_uuid,

            "APPROVED",

            approved_by,

            actor_role,

            "Signalement local approuvé."

        )


        return self.find_by_uuid(
            entry_uuid
        )


    def find_by_uuid(
        self,
        entry_uuid
    ):

        with self.lock:

            row = self.connection.execute(
                """
                SELECT *
                FROM watchlist_entries
                WHERE uuid=?
                """,
                (
                    entry_uuid,
                )
            ).fetchone()


        return (
            dict(row)
            if row
            else None
        )


    def expire_due(
        self
    ):

        now = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT uuid
                FROM watchlist_entries

                WHERE status='ACTIVE'

                  AND valid_until IS NOT NULL

                  AND TRIM(
                      valid_until
                  ) != ''

                  AND valid_until <= ?
                """,
                (
                    now,
                )
            ).fetchall()


            expired = [
                row["uuid"]
                for row in rows
            ]


            for entry_uuid in expired:

                self.connection.execute(
                    """
                    UPDATE watchlist_entries

                    SET
                        status='EXPIRED',
                        updated_at=?

                    WHERE uuid=?
                      AND status='ACTIVE'
                    """,
                    (
                        now,
                        entry_uuid
                    )
                )


            self.connection.commit()


        for entry_uuid in expired:

            self.add_audit(

                entry_uuid,

                "EXPIRED",

                "SYSTEM",

                "SYSTEM",

                "Expiration automatique de la surveillance."

            )


        return len(
            expired
        )


    def active_by_plate(
        self,
        plate
    ):

        self.expire_due()


        plate = self.normalize_plate(
            plate
        )


        now = (
            datetime.now()
            .isoformat()
        )


        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *
                FROM watchlist_entries

                WHERE plate=?
                  AND status='ACTIVE'

                  AND (
                      valid_from IS NULL
                      OR
                      TRIM(valid_from) = ''
                      OR
                      valid_from <= ?
                  )

                  AND (
                      valid_until IS NULL
                      OR
                      TRIM(valid_until) = ''
                      OR
                      valid_until > ?
                  )

                ORDER BY created_at DESC
                """,
                (
                    plate,
                    now,
                    now
                )
            ).fetchall()


        return [
            dict(row)
            for row in rows
        ]


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
                FROM watchlist_entries

                ORDER BY created_at DESC

                LIMIT ?
                """,
                (
                    limit,
                )
            ).fetchall()


        return [
            dict(row)
            for row in rows
        ]


    def audit_for_entry(
        self,
        entry_uuid
    ):

        with self.lock:

            rows = self.connection.execute(
                """
                SELECT *
                FROM watchlist_audit

                WHERE entry_uuid=?

                ORDER BY timestamp ASC
                """,
                (
                    entry_uuid,
                )
            ).fetchall()


        return [
            dict(row)
            for row in rows
        ]


watchlist_database = (
    WatchlistDatabase()
)
