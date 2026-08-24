"""
========================================================
PHOENIX VISION AI

Enterprise Settings Database

Persistent local configuration with tamper-evident audit.

Phoenix Security Technologies
========================================================
"""

import hashlib
import json
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from uuid import uuid4


class SettingsDatabase:

    SCHEMA_VERSION = "1"

    SUPPORTED_TYPES = {
        "string",
        "integer",
        "float",
        "boolean",
        "list",
        "object",
        "null",
    }


    def __init__(
        self,
        path="data/settings.db",
    ):

        self.path = Path(
            path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()


    # ==================================================
    # CONNECTION
    # ==================================================

    def _connect(
        self,
    ):

        connection = sqlite3.connect(
            str(
                self.path
            ),
            timeout=10,
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            "PRAGMA busy_timeout = 5000"
        )

        return connection


    # ==================================================
    # INITIALIZATION
    # ==================================================

    def _initialize(
        self,
    ):

        with self._connect() as connection:

            connection.execute(
                "PRAGMA journal_mode = WAL"
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                settings_meta (
                    meta_key TEXT PRIMARY KEY,
                    meta_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                settings (
                    setting_key TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    source TEXT NOT NULL,
                    mutable INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    updated_role TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                settings_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT NOT NULL UNIQUE,
                    setting_key TEXT NOT NULL,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    actor_role TEXT NOT NULL,
                    previous_value_json TEXT,
                    new_value_json TEXT,
                    revision INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_settings_category
                ON settings(category)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_settings_audit_key
                ON settings_audit(
                    setting_key,
                    id
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_settings_audit_timestamp
                ON settings_audit(timestamp)
                """
            )

            now = self._now()

            connection.execute(
                """
                INSERT OR IGNORE INTO
                settings_meta (
                    meta_key,
                    meta_value,
                    updated_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    "schema_version",
                    self.SCHEMA_VERSION,
                    now,
                ),
            )


    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _now(
        self=None,
    ):

        return (
            datetime.now(
                timezone.utc
            )
            .isoformat()
        )


    @staticmethod
    def _canonical_json(
        value,
    ):

        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )


    @classmethod
    def _encode_value(
        cls,
        value,
    ):

        return cls._canonical_json(
            value
        )


    @staticmethod
    def _decode_value(
        value_json,
    ):

        if value_json is None:

            return None

        return json.loads(
            value_json
        )


    @staticmethod
    def _normalize_text(
        value,
        field_name,
    ):

        value = str(
            value
            or
            ""
        ).strip()

        if not value:

            raise ValueError(
                f"{field_name} est obligatoire."
            )

        return value


    @classmethod
    def _infer_type(
        cls,
        value,
    ):

        if value is None:

            return "null"

        if isinstance(
            value,
            bool,
        ):

            return "boolean"

        if isinstance(
            value,
            int,
        ):

            return "integer"

        if isinstance(
            value,
            float,
        ):

            return "float"

        if isinstance(
            value,
            str,
        ):

            return "string"

        if isinstance(
            value,
            list,
        ):

            return "list"

        if isinstance(
            value,
            dict,
        ):

            return "object"

        raise TypeError(
            (
                "Type de paramètre non supporté : "
                f"{type(value).__name__}"
            )
        )


    @classmethod
    def _normalize_data_type(
        cls,
        data_type,
        value,
    ):

        if data_type is None:

            data_type = cls._infer_type(
                value
            )

        data_type = str(
            data_type
        ).strip().lower()

        if (
            data_type
            not in cls.SUPPORTED_TYPES
        ):

            raise ValueError(
                (
                    "Type de donnée non supporté : "
                    f"{data_type}"
                )
            )

        return data_type


    @staticmethod
    def _row_to_setting(
        row,
    ):

        if row is None:

            return None

        return {
            "key":
                row["setting_key"],

            "category":
                row["category"],

            "value":
                SettingsDatabase
                ._decode_value(
                    row["value_json"]
                ),

            "data_type":
                row["data_type"],

            "scope":
                row["scope"],

            "source":
                row["source"],

            "mutable":
                bool(
                    row["mutable"]
                ),

            "description":
                row["description"],

            "revision":
                row["revision"],

            "created_at":
                row["created_at"],

            "updated_at":
                row["updated_at"],

            "updated_by":
                row["updated_by"],

            "updated_role":
                row["updated_role"],
        }


    @staticmethod
    def _row_to_audit(
        row,
    ):

        if row is None:

            return None

        return {
            "id":
                row["id"],

            "uuid":
                row["uuid"],

            "setting_key":
                row["setting_key"],

            "category":
                row["category"],

            "action":
                row["action"],

            "actor":
                row["actor"],

            "actor_role":
                row["actor_role"],

            "previous_value":
                SettingsDatabase
                ._decode_value(
                    row[
                        "previous_value_json"
                    ]
                ),

            "new_value":
                SettingsDatabase
                ._decode_value(
                    row[
                        "new_value_json"
                    ]
                ),

            "revision":
                row["revision"],

            "timestamp":
                row["timestamp"],

            "details":
                SettingsDatabase
                ._decode_value(
                    row["details_json"]
                ),

            "previous_hash":
                row["previous_hash"],

            "event_hash":
                row["event_hash"],
        }


    # ==================================================
    # AUDIT HASH CHAIN
    # ==================================================

    def _append_audit(
        self,
        connection,
        *,
        setting_key,
        category,
        action,
        actor,
        actor_role,
        previous_value_json,
        new_value_json,
        revision,
        details=None,
    ):

        previous = connection.execute(
            """
            SELECT event_hash
            FROM settings_audit
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        previous_hash = (
            previous["event_hash"]
            if previous
            else
            ""
        )

        event_uuid = str(
            uuid4()
        )

        timestamp = self._now()

        details_json = (
            self._canonical_json(
                details
                or
                {}
            )
        )

        payload = {
            "uuid":
                event_uuid,

            "setting_key":
                setting_key,

            "category":
                category,

            "action":
                action,

            "actor":
                actor,

            "actor_role":
                actor_role,

            "previous_value_json":
                previous_value_json,

            "new_value_json":
                new_value_json,

            "revision":
                revision,

            "timestamp":
                timestamp,

            "details_json":
                details_json,

            "previous_hash":
                previous_hash,
        }

        event_hash = (
            hashlib.sha256(
                self._canonical_json(
                    payload
                ).encode(
                    "utf-8"
                )
            )
            .hexdigest()
        )

        connection.execute(
            """
            INSERT INTO settings_audit (
                uuid,
                setting_key,
                category,
                action,
                actor,
                actor_role,
                previous_value_json,
                new_value_json,
                revision,
                timestamp,
                details_json,
                previous_hash,
                event_hash
            )
            VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                event_uuid,
                setting_key,
                category,
                action,
                actor,
                actor_role,
                previous_value_json,
                new_value_json,
                revision,
                timestamp,
                details_json,
                previous_hash,
                event_hash,
            ),
        )

        return event_hash


    # ==================================================
    # READ
    # ==================================================

    def get(
        self,
        setting_key,
    ):

        setting_key = (
            self._normalize_text(
                setting_key,
                "setting_key",
            )
        )

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM settings
                WHERE setting_key = ?
                """,
                (
                    setting_key,
                ),
            ).fetchone()

        return self._row_to_setting(
            row
        )


    def exists(
        self,
        setting_key,
    ):

        return (
            self.get(
                setting_key
            )
            is not None
        )


    def all(
        self,
    ):

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM settings
                ORDER BY
                    category,
                    setting_key
                """
            ).fetchall()

        return [
            self._row_to_setting(
                row
            )
            for row in rows
        ]


    def by_category(
        self,
        category,
    ):

        category = (
            self._normalize_text(
                category,
                "category",
            )
            .upper()
        )

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM settings
                WHERE category = ?
                ORDER BY setting_key
                """,
                (
                    category,
                ),
            ).fetchall()

        return [
            self._row_to_setting(
                row
            )
            for row in rows
        ]


    # ==================================================
    # WRITE
    # ==================================================

    def set(
        self,
        setting_key,
        value,
        *,
        category,
        actor,
        actor_role,
        data_type=None,
        scope="LOCAL",
        source="LOCAL",
        mutable=True,
        description="",
        details=None,
        force=False,
    ):

        setting_key = (
            self._normalize_text(
                setting_key,
                "setting_key",
            )
        )

        category = (
            self._normalize_text(
                category,
                "category",
            )
            .upper()
        )

        actor = self._normalize_text(
            actor,
            "actor",
        )

        actor_role = (
            self._normalize_text(
                actor_role,
                "actor_role",
            )
            .upper()
        )

        scope = (
            self._normalize_text(
                scope,
                "scope",
            )
            .upper()
        )

        source = (
            self._normalize_text(
                source,
                "source",
            )
            .upper()
        )

        data_type = (
            self._normalize_data_type(
                data_type,
                value,
            )
        )

        description = str(
            description
            or
            ""
        ).strip()

        value_json = (
            self._encode_value(
                value
            )
        )

        now = self._now()

        with self._connect() as connection:

            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = (
                connection.execute(
                    """
                    SELECT *
                    FROM settings
                    WHERE setting_key = ?
                    """,
                    (
                        setting_key,
                    ),
                )
                .fetchone()
            )

            if existing:

                if (
                    not bool(
                        existing["mutable"]
                    )
                    and
                    not force
                ):

                    raise PermissionError(
                        (
                            "Paramètre en lecture "
                            "seule : "
                            f"{setting_key}"
                        )
                    )

                current_state = (
                    existing["value_json"],
                    existing["category"],
                    existing["data_type"],
                    existing["scope"],
                    existing["source"],
                    bool(
                        existing["mutable"]
                    ),
                    existing["description"],
                )

                requested_state = (
                    value_json,
                    category,
                    data_type,
                    scope,
                    source,
                    bool(
                        mutable
                    ),
                    description,
                )

                if (
                    current_state
                    ==
                    requested_state
                ):

                    result = (
                        self._row_to_setting(
                            existing
                        )
                    )

                    result["changed"] = (
                        False
                    )

                    return result

                revision = (
                    int(
                        existing[
                            "revision"
                        ]
                    )
                    +
                    1
                )

                created_at = (
                    existing[
                        "created_at"
                    ]
                )

                previous_value_json = (
                    existing[
                        "value_json"
                    ]
                )

                action = "UPDATED"

            else:

                revision = 1

                created_at = now

                previous_value_json = None

                action = "CREATED"


            connection.execute(
                """
                INSERT INTO settings (
                    setting_key,
                    category,
                    value_json,
                    data_type,
                    scope,
                    source,
                    mutable,
                    description,
                    revision,
                    created_at,
                    updated_at,
                    updated_by,
                    updated_role
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                ON CONFLICT(setting_key)
                DO UPDATE SET
                    category =
                        excluded.category,

                    value_json =
                        excluded.value_json,

                    data_type =
                        excluded.data_type,

                    scope =
                        excluded.scope,

                    source =
                        excluded.source,

                    mutable =
                        excluded.mutable,

                    description =
                        excluded.description,

                    revision =
                        excluded.revision,

                    updated_at =
                        excluded.updated_at,

                    updated_by =
                        excluded.updated_by,

                    updated_role =
                        excluded.updated_role
                """,
                (
                    setting_key,
                    category,
                    value_json,
                    data_type,
                    scope,
                    source,
                    int(
                        bool(
                            mutable
                        )
                    ),
                    description,
                    revision,
                    created_at,
                    now,
                    actor,
                    actor_role,
                ),
            )

            self._append_audit(
                connection,
                setting_key=
                    setting_key,

                category=
                    category,

                action=
                    action,

                actor=
                    actor,

                actor_role=
                    actor_role,

                previous_value_json=
                    previous_value_json,

                new_value_json=
                    value_json,

                revision=
                    revision,

                details=
                    details,
            )

            row = connection.execute(
                """
                SELECT *
                FROM settings
                WHERE setting_key = ?
                """,
                (
                    setting_key,
                ),
            ).fetchone()

        result = self._row_to_setting(
            row
        )

        result["changed"] = True

        return result


    # ==================================================
    # DELETE
    # ==================================================

    def delete(
        self,
        setting_key,
        *,
        actor,
        actor_role,
        details=None,
        force=False,
    ):

        setting_key = (
            self._normalize_text(
                setting_key,
                "setting_key",
            )
        )

        actor = self._normalize_text(
            actor,
            "actor",
        )

        actor_role = (
            self._normalize_text(
                actor_role,
                "actor_role",
            )
            .upper()
        )

        with self._connect() as connection:

            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = (
                connection.execute(
                    """
                    SELECT *
                    FROM settings
                    WHERE setting_key = ?
                    """,
                    (
                        setting_key,
                    ),
                )
                .fetchone()
            )

            if existing is None:

                return False

            if (
                not bool(
                    existing["mutable"]
                )
                and
                not force
            ):

                raise PermissionError(
                    (
                        "Paramètre en lecture "
                        "seule : "
                        f"{setting_key}"
                    )
                )

            revision = (
                int(
                    existing[
                        "revision"
                    ]
                )
                +
                1
            )

            connection.execute(
                """
                DELETE FROM settings
                WHERE setting_key = ?
                """,
                (
                    setting_key,
                ),
            )

            self._append_audit(
                connection,
                setting_key=
                    setting_key,

                category=
                    existing[
                        "category"
                    ],

                action=
                    "DELETED",

                actor=
                    actor,

                actor_role=
                    actor_role,

                previous_value_json=
                    existing[
                        "value_json"
                    ],

                new_value_json=
                    None,

                revision=
                    revision,

                details=
                    details,
            )

        return True


    # ==================================================
    # AUDIT
    # ==================================================

    def audit_for_setting(
        self,
        setting_key,
        limit=200,
    ):

        setting_key = (
            self._normalize_text(
                setting_key,
                "setting_key",
            )
        )

        limit = max(
            1,
            min(
                int(
                    limit
                ),
                1000,
            ),
        )

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM settings_audit
                WHERE setting_key = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    setting_key,
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_audit(
                row
            )
            for row in rows
        ]


    def recent_audit(
        self,
        limit=100,
    ):

        limit = max(
            1,
            min(
                int(
                    limit
                ),
                1000,
            ),
        )

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM settings_audit
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    limit,
                ),
            ).fetchall()

        return [
            self._row_to_audit(
                row
            )
            for row in rows
        ]


    def verify_audit_chain(
        self,
    ):

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM settings_audit
                ORDER BY id ASC
                """
            ).fetchall()

        expected_previous_hash = ""

        for row in rows:

            if (
                row["previous_hash"]
                !=
                expected_previous_hash
            ):

                return {
                    "valid": False,
                    "events":
                        len(
                            rows
                        ),
                    "failed_id":
                        row["id"],
                    "reason":
                        "PREVIOUS_HASH_MISMATCH",
                }

            payload = {
                "uuid":
                    row["uuid"],

                "setting_key":
                    row["setting_key"],

                "category":
                    row["category"],

                "action":
                    row["action"],

                "actor":
                    row["actor"],

                "actor_role":
                    row["actor_role"],

                "previous_value_json":
                    row[
                        "previous_value_json"
                    ],

                "new_value_json":
                    row[
                        "new_value_json"
                    ],

                "revision":
                    row["revision"],

                "timestamp":
                    row["timestamp"],

                "details_json":
                    row["details_json"],

                "previous_hash":
                    row["previous_hash"],
            }

            calculated_hash = (
                hashlib.sha256(
                    self._canonical_json(
                        payload
                    ).encode(
                        "utf-8"
                    )
                )
                .hexdigest()
            )

            if (
                calculated_hash
                !=
                row["event_hash"]
            ):

                return {
                    "valid": False,
                    "events":
                        len(
                            rows
                        ),
                    "failed_id":
                        row["id"],
                    "reason":
                        "EVENT_HASH_MISMATCH",
                }

            expected_previous_hash = (
                row["event_hash"]
            )

        return {
            "valid": True,
            "events":
                len(
                    rows
                ),
            "failed_id":
                None,
            "reason":
                None,
        }


    # ==================================================
    # STATISTICS
    # ==================================================

    def stats(
        self,
    ):

        with self._connect() as connection:

            total = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM settings
                """
            ).fetchone()["total"]

            read_only = (
                connection.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM settings
                    WHERE mutable = 0
                    """
                )
                .fetchone()["total"]
            )

            audit_events = (
                connection.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM settings_audit
                    """
                )
                .fetchone()["total"]
            )

            categories = (
                connection.execute(
                    """
                    SELECT
                        category,
                        COUNT(*) AS total
                    FROM settings
                    GROUP BY category
                    ORDER BY category
                    """
                )
                .fetchall()
            )

        return {
            "total":
                total,

            "read_only":
                read_only,

            "mutable":
                total
                -
                read_only,

            "audit_events":
                audit_events,

            "categories": {
                row["category"]:
                    row["total"]
                for row
                in categories
            },
        }


settings_database = SettingsDatabase()
