"""
============================================================
PHOENIX VISION AI
Enterprise User Registry Database

IMPORTANT:
- No password hash is stored here.
- No password salt is stored here.
- Authentication remains separated from administration.
============================================================
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid

from datetime import datetime
from pathlib import Path


DEFAULT_DATABASE_PATH = Path(
    "data/users.db"
)


USER_COLUMNS = (
    "request_id",
    "username",
    "display_name",
    "nom",
    "postnom",
    "prenom",
    "sexe",
    "date_naissance",
    "email",
    "telephone",
    "organisation",
    "matricule",
    "departement",
    "fonction",
    "site_affectation",
    "responsable",
    "requested_access",
    "request_reason",
    "role",
    "access_level",
    "status",
    "photo_url",
    "account_expiry",
    "must_change_password",
    "approved_at",
    "approved_by",
    "account_created_at",
    "password_changed_at",
    "last_login_at",
    "suspended_at",
    "suspended_by",
    "suspension_reason",
    "disabled_at",
    "disabled_by",
    "disable_reason",
)


def utc_timestamp():

    return (
        datetime.now()
        .astimezone()
        .isoformat(
            timespec="seconds"
        )
    )


def canonical_json(
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


class UserDatabase:

    SCHEMA_VERSION = "1"


    def __init__(
        self,
        path=DEFAULT_DATABASE_PATH,
    ):

        self.path = Path(
            path
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()


    def connect(
        self,
    ):

        connection = sqlite3.connect(
            self.path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        return connection


    def initialize(
        self,
    ):

        with self.connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_registry_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                INSERT INTO user_registry_meta(
                    key,
                    value
                )
                VALUES(
                    'schema_version',
                    ?
                )
                ON CONFLICT(key)
                DO UPDATE SET
                    value = excluded.value
                """,
                (
                    self.SCHEMA_VERSION,
                ),
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,

                    request_id TEXT,

                    username TEXT NOT NULL
                        UNIQUE,

                    display_name TEXT,

                    nom TEXT,
                    postnom TEXT,
                    prenom TEXT,

                    sexe TEXT,
                    date_naissance TEXT,

                    email TEXT,
                    telephone TEXT,

                    organisation TEXT,
                    matricule TEXT,
                    departement TEXT,
                    fonction TEXT,
                    site_affectation TEXT,
                    responsable TEXT,

                    requested_access TEXT,
                    request_reason TEXT,

                    role TEXT NOT NULL,
                    access_level TEXT,

                    status TEXT NOT NULL,

                    photo_url TEXT,

                    account_expiry TEXT,

                    must_change_password INTEGER
                        NOT NULL DEFAULT 0,

                    approved_at TEXT,
                    approved_by TEXT,

                    account_created_at TEXT,
                    password_changed_at TEXT,
                    last_login_at TEXT,

                    suspended_at TEXT,
                    suspended_by TEXT,
                    suspension_reason TEXT,

                    disabled_at TEXT,
                    disabled_by TEXT,
                    disable_reason TEXT,

                    revision INTEGER
                        NOT NULL DEFAULT 1,

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )


            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                    idx_users_request_id
                ON users(request_id)
                WHERE request_id IS NOT NULL
                  AND request_id != ''
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_users_role
                ON users(role)
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_users_status
                ON users(status)
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_audit (
                    event_id INTEGER PRIMARY KEY
                        AUTOINCREMENT,

                    user_id TEXT NOT NULL,

                    action TEXT NOT NULL,

                    actor_username TEXT NOT NULL,
                    actor_role TEXT NOT NULL,

                    reason TEXT,

                    metadata_json TEXT NOT NULL,

                    created_at TEXT NOT NULL,

                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                        REFERENCES users(user_id)
                )
                """
            )


    def _new_user_id(
        self,
    ):

        return (
            "USR-"
            +
            uuid.uuid4()
            .hex[:12]
            .upper()
        )


    def _audit_hash(
        self,
        payload,
        previous_hash,
    ):

        material = (
            previous_hash
            +
            "|"
            +
            canonical_json(
                payload
            )
        )

        return hashlib.sha256(
            material.encode(
                "utf-8"
            )
        ).hexdigest()


    def _append_audit(
        self,
        connection,
        *,
        user_id,
        action,
        actor_username,
        actor_role,
        reason="",
        metadata=None,
    ):

        row = connection.execute(
            """
            SELECT event_hash
            FROM user_audit
            ORDER BY event_id DESC
            LIMIT 1
            """
        ).fetchone()


        previous_hash = (
            row["event_hash"]
            if row
            else
            "GENESIS"
        )


        created_at = utc_timestamp()


        payload = {
            "user_id":
                user_id,

            "action":
                action,

            "actor_username":
                str(
                    actor_username
                    or
                    "SYSTEM"
                ),

            "actor_role":
                str(
                    actor_role
                    or
                    "SYSTEM"
                ).upper(),

            "reason":
                str(
                    reason
                    or
                    ""
                ),

            "metadata":
                metadata
                or
                {},

            "created_at":
                created_at,
        }


        event_hash = self._audit_hash(
            payload,
            previous_hash,
        )


        connection.execute(
            """
            INSERT INTO user_audit(
                user_id,
                action,
                actor_username,
                actor_role,
                reason,
                metadata_json,
                created_at,
                previous_hash,
                event_hash
            )
            VALUES(
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                user_id,
                payload["action"],
                payload["actor_username"],
                payload["actor_role"],
                payload["reason"],
                canonical_json(
                    payload["metadata"]
                ),
                created_at,
                previous_hash,
                event_hash,
            ),
        )


    def upsert_user(
        self,
        record,
        *,
        actor_username="SYSTEM",
        actor_role="SYSTEM",
        reason="Registry synchronization",
    ):

        username = str(
            record.get(
                "username"
            )
            or
            ""
        ).strip()


        if not username:

            raise ValueError(
                "username is required"
            )


        with self.connect() as connection:

            existing = connection.execute(
                """
                SELECT *
                FROM users
                WHERE lower(username) =
                    lower(?)
                LIMIT 1
                """,
                (
                    username,
                ),
            ).fetchone()


            now = utc_timestamp()


            normalized = {}

            for column in USER_COLUMNS:

                value = record.get(
                    column
                )

                if column == "must_change_password":

                    normalized[column] = (
                        1
                        if bool(value)
                        else
                        0
                    )

                else:

                    normalized[column] = (
                        value
                        if value is not None
                        else
                        ""
                    )


            normalized[
                "username"
            ] = username


            if existing is None:

                user_id = (
                    self._new_user_id()
                )

                placeholders = ", ".join(
                    "?"
                    for _
                    in USER_COLUMNS
                )

                columns = ", ".join(
                    USER_COLUMNS
                )

                values = [
                    normalized[column]
                    for column
                    in USER_COLUMNS
                ]


                connection.execute(
                    f"""
                    INSERT INTO users(
                        user_id,
                        {columns},
                        revision,
                        created_at,
                        updated_at
                    )
                    VALUES(
                        ?,
                        {placeholders},
                        1,
                        ?,
                        ?
                    )
                    """,
                    [
                        user_id,
                        *values,
                        now,
                        now,
                    ],
                )


                self._append_audit(
                    connection,
                    user_id=
                        user_id,
                    action=
                        "USER_CREATED",
                    actor_username=
                        actor_username,
                    actor_role=
                        actor_role,
                    reason=
                        reason,
                    metadata={
                        "role":
                            normalized[
                                "role"
                            ],

                        "status":
                            normalized[
                                "status"
                            ],

                        "source":
                            "LEGACY_ACCOUNT_SYNC",
                    },
                )


                return {
                    "action":
                        "CREATED",

                    "user_id":
                        user_id,

                    "username":
                        username,
                }


            user_id = (
                existing[
                    "user_id"
                ]
            )


            # =================================================
            # PROTECTION DU CYCLE DE VIE ADMINISTRATIF
            # =================================================
            #
            # Une synchronisation depuis approved_users.json
            # ne doit jamais effacer les informations qui
            # appartiennent au registre administratif.
            #

            preserved_fields = (
                "last_login_at",
                "suspended_at",
                "suspended_by",
                "suspension_reason",
                "disabled_at",
                "disabled_by",
                "disable_reason",
            )


            for field in preserved_fields:

                normalized[
                    field
                ] = (
                    existing[
                        field
                    ]
                    if existing[
                        field
                    ] is not None
                    else
                    ""
                )


            existing_status = str(
                existing[
                    "status"
                ]
                or
                ""
            ).strip().upper()


            if existing_status in {
                "SUSPENDED",
                "DISABLED",
            }:

                normalized[
                    "status"
                ] = existing_status


            changed_fields = []

            for column in USER_COLUMNS:

                previous = (
                    existing[
                        column
                    ]
                )

                current = (
                    normalized[
                        column
                    ]
                )


                if str(
                    previous
                    if previous is not None
                    else
                    ""
                ) != str(
                    current
                    if current is not None
                    else
                    ""
                ):

                    changed_fields.append(
                        column
                    )


            if not changed_fields:

                return {
                    "action":
                        "UNCHANGED",

                    "user_id":
                        user_id,

                    "username":
                        username,
                }


            assignments = ", ".join(
                f"{column} = ?"
                for column
                in USER_COLUMNS
            )

            values = [
                normalized[column]
                for column
                in USER_COLUMNS
            ]


            connection.execute(
                f"""
                UPDATE users
                SET
                    {assignments},
                    revision =
                        revision + 1,
                    updated_at = ?
                WHERE user_id = ?
                """,
                [
                    *values,
                    now,
                    user_id,
                ],
            )


            self._append_audit(
                connection,
                user_id=
                    user_id,
                action=
                    "USER_SYNCHRONIZED",
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
                metadata={
                    "changed_fields":
                        changed_fields,

                    "previous_role":
                        existing[
                            "role"
                        ],

                    "new_role":
                        normalized[
                            "role"
                        ],

                    "previous_status":
                        existing[
                            "status"
                        ],

                    "new_status":
                        normalized[
                            "status"
                        ],
                },
            )


            return {
                "action":
                    "UPDATED",

                "user_id":
                    user_id,

                "username":
                    username,

                "changed_fields":
                    changed_fields,
            }


    def update_user_fields(
        self,
        username,
        changes,
        *,
        action,
        actor_username,
        actor_role,
        reason="",
        metadata=None,
    ):

        username = str(
            username
            or
            ""
        ).strip()


        if not username:

            raise ValueError(
                "username is required"
            )


        allowed_fields = (
            set(
                USER_COLUMNS
            )
            -
            {
                "username",
                "request_id",
            }
        )


        invalid_fields = (
            set(
                changes.keys()
            )
            -
            allowed_fields
        )


        if invalid_fields:

            raise ValueError(
                "Invalid user fields: "
                +
                ", ".join(
                    sorted(
                        invalid_fields
                    )
                )
            )


        with self.connect() as connection:

            existing = connection.execute(
                """
                SELECT *
                FROM users
                WHERE lower(username) =
                    lower(?)
                LIMIT 1
                """,
                (
                    username,
                ),
            ).fetchone()


            if existing is None:

                return {
                    "action":
                        "NOT_FOUND",

                    "username":
                        username,
                }


            normalized = {}

            changed_fields = []


            for field, value in changes.items():

                if field == "must_change_password":

                    current = (
                        1
                        if bool(
                            value
                        )
                        else
                        0
                    )

                else:

                    current = (
                        value
                        if value is not None
                        else
                        ""
                    )


                previous = (
                    existing[
                        field
                    ]
                )


                normalized[
                    field
                ] = current


                if str(
                    previous
                    if previous is not None
                    else
                    ""
                ) != str(
                    current
                    if current is not None
                    else
                    ""
                ):

                    changed_fields.append(
                        field
                    )


            if not changed_fields:

                return {
                    "action":
                        "UNCHANGED",

                    "user_id":
                        existing[
                            "user_id"
                        ],

                    "username":
                        username,
                }


            assignments = ", ".join(
                f"{field} = ?"
                for field
                in changed_fields
            )


            values = [
                normalized[
                    field
                ]
                for field
                in changed_fields
            ]


            now = utc_timestamp()


            connection.execute(
                f"""
                UPDATE users
                SET
                    {assignments},
                    revision =
                        revision + 1,
                    updated_at = ?
                WHERE user_id = ?
                """,
                [
                    *values,
                    now,
                    existing[
                        "user_id"
                    ],
                ],
            )


            event_metadata = {
                "changed_fields":
                    changed_fields,
            }


            if (
                "status"
                in
                changed_fields
            ):

                event_metadata[
                    "previous_status"
                ] = existing[
                    "status"
                ]

                event_metadata[
                    "new_status"
                ] = normalized[
                    "status"
                ]


            if (
                "role"
                in
                changed_fields
            ):

                event_metadata[
                    "previous_role"
                ] = existing[
                    "role"
                ]

                event_metadata[
                    "new_role"
                ] = normalized[
                    "role"
                ]


            if metadata:

                event_metadata[
                    "details"
                ] = metadata


            self._append_audit(
                connection,
                user_id=
                    existing[
                        "user_id"
                    ],
                action=
                    action,
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
                metadata=
                    event_metadata,
            )


            return {
                "action":
                    "UPDATED",

                "user_id":
                    existing[
                        "user_id"
                    ],

                "username":
                    username,

                "changed_fields":
                    changed_fields,
            }


    def list_users(
        self,
        *,
        limit=500,
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM users
                ORDER BY
                    display_name COLLATE NOCASE,
                    username COLLATE NOCASE
                LIMIT ?
                """,
                (
                    int(
                        limit
                    ),
                ),
            ).fetchall()


            return [
                dict(
                    row
                )
                for row
                in rows
            ]


    def get_user(
        self,
        username,
    ):

        with self.connect() as connection:

            row = connection.execute(
                """
                SELECT *
                FROM users
                WHERE lower(username) =
                    lower(?)
                LIMIT 1
                """,
                (
                    str(
                        username
                    ),
                ),
            ).fetchone()


            return (
                dict(
                    row
                )
                if row
                else
                None
            )


    def audit_events(
        self,
        *,
        limit=200,
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM user_audit
                ORDER BY event_id DESC
                LIMIT ?
                """,
                (
                    int(
                        limit
                    ),
                ),
            ).fetchall()


            return [
                dict(
                    row
                )
                for row
                in rows
            ]


    def record_audit_event(
        self,
        username,
        *,
        action,
        actor_username,
        actor_role,
        reason="",
        metadata=None,
    ):

        with self.connect() as connection:

            user = connection.execute(
                """
                SELECT user_id
                FROM users
                WHERE lower(username) =
                    lower(?)
                LIMIT 1
                """,
                (
                    str(
                        username
                    ),
                ),
            ).fetchone()


            if user is None:

                return {
                    "action":
                        "NOT_FOUND",

                    "username":
                        username,
                }


            self._append_audit(
                connection,
                user_id=
                    user[
                        "user_id"
                    ],
                action=
                    action,
                actor_username=
                    actor_username,
                actor_role=
                    actor_role,
                reason=
                    reason,
                metadata=
                    metadata
                    or
                    {},
            )


            return {
                "action":
                    "RECORDED",

                "username":
                    username,

                "user_id":
                    user[
                        "user_id"
                    ],
            }


    def audit_events_for_user(
        self,
        username,
        *,
        limit=200,
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    audit.*
                FROM user_audit AS audit
                INNER JOIN users AS user
                    ON user.user_id = audit.user_id
                WHERE lower(user.username) =
                    lower(?)
                ORDER BY audit.event_id DESC
                LIMIT ?
                """,
                (
                    str(
                        username
                    ),
                    int(
                        limit
                    ),
                ),
            ).fetchall()


        result = []

        for row in rows:

            item = dict(
                row
            )

            try:

                item[
                    "metadata"
                ] = json.loads(
                    item.get(
                        "metadata_json"
                    )
                    or
                    "{}"
                )

            except (
                json.JSONDecodeError,
                TypeError,
            ):

                item[
                    "metadata"
                ] = {}


            item.pop(
                "metadata_json",
                None,
            )


            result.append(
                item
            )


        return result


    def verify_audit_chain(
        self,
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM user_audit
                ORDER BY event_id ASC
                """
            ).fetchall()


        previous_hash = (
            "GENESIS"
        )


        for row in rows:

            if (
                row["previous_hash"]
                !=
                previous_hash
            ):

                return False


            payload = {
                "user_id":
                    row[
                        "user_id"
                    ],

                "action":
                    row[
                        "action"
                    ],

                "actor_username":
                    row[
                        "actor_username"
                    ],

                "actor_role":
                    row[
                        "actor_role"
                    ],

                "reason":
                    row[
                        "reason"
                    ]
                    or
                    "",

                "metadata":
                    json.loads(
                        row[
                            "metadata_json"
                        ]
                    ),

                "created_at":
                    row[
                        "created_at"
                    ],
            }


            expected = (
                self._audit_hash(
                    payload,
                    previous_hash,
                )
            )


            if (
                expected
                !=
                row[
                    "event_hash"
                ]
            ):

                return False


            previous_hash = (
                row[
                    "event_hash"
                ]
            )


        return True


user_database = UserDatabase()
