"""
============================================================
PHOENIX VISION AI

Enterprise System Diagnostics

Diagnostics locaux, non destructifs et auditables.

Phoenix Security Technologies
============================================================
"""

from __future__ import annotations

import hashlib
import json
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core.system.system_health import (
    PROJECT_ROOT,
    STATUS_ONLINE,
    STATUS_AVAILABLE,
    STATUS_UNAVAILABLE,
    system_health_service,
)


PASS = "OK"
WARNING = "ATTENTION"
FAIL = "ECHEC"


def utc_now_iso():

    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )


class SystemDiagnosticsService:

    def __init__(
        self,
        *,
        project_root=PROJECT_ROOT,
    ):

        self.project_root = Path(
            project_root
        ).resolve()

        self.data_directory = (
            self.project_root
            /
            "data"
        )

        self.audit_database = (
            self.data_directory
            /
            "system_diagnostics.db"
        )

        self._ensure_audit_database()


    # ========================================================
    # AUDIT DATABASE
    # ========================================================

    def _connect_audit(
        self,
    ):

        self.data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = sqlite3.connect(
            str(
                self.audit_database
            ),
            timeout=3.0,
        )

        connection.row_factory = (
            sqlite3.Row
        )

        return connection


    def _ensure_audit_database(
        self,
    ):

        with self._connect_audit() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS
                system_diagnostic_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    target TEXT,
                    result TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                )
                """
            )

            connection.commit()


    def _last_hash(
        self,
        connection,
    ):

        row = connection.execute(
            """
            SELECT event_hash
            FROM system_diagnostic_audit
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        if row is None:

            return "GENESIS"

        return str(
            row[
                "event_hash"
            ]
        )


    def record_event(
        self,
        *,
        action,
        actor,
        result,
        details=None,
        target=None,
    ):

        created_at = utc_now_iso()

        details = (
            details
            if isinstance(
                details,
                dict,
            )
            else {}
        )

        with self._connect_audit() as connection:

            previous_hash = (
                self._last_hash(
                    connection
                )
            )

            payload = {
                "action":
                    str(
                        action
                    ),

                "actor":
                    str(
                        actor
                    ),

                "target":
                    (
                        str(
                            target
                        )
                        if target
                        else None
                    ),

                "result":
                    str(
                        result
                    ),

                "details":
                    details,

                "created_at":
                    created_at,

                "previous_hash":
                    previous_hash,
            }

            canonical = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
            )

            event_hash = (
                hashlib.sha256(
                    canonical.encode(
                        "utf-8"
                    )
                )
                .hexdigest()
            )

            connection.execute(
                """
                INSERT INTO
                system_diagnostic_audit (
                    action,
                    actor,
                    target,
                    result,
                    details_json,
                    created_at,
                    previous_hash,
                    event_hash
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload[
                        "action"
                    ],
                    payload[
                        "actor"
                    ],
                    payload[
                        "target"
                    ],
                    payload[
                        "result"
                    ],
                    json.dumps(
                        details,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    created_at,
                    previous_hash,
                    event_hash,
                ),
            )

            connection.commit()

        return event_hash


    # ========================================================
    # DIAGNOSTIC GÉNÉRAL
    # ========================================================

    def run_general(
        self,
        *,
        actor,
    ):

        health = (
            system_health_service
            .snapshot()
        )

        checks = []


        def add(
            key,
            label,
            result,
            message,
        ):

            checks.append(
                {
                    "key":
                        key,

                    "label":
                        label,

                    "result":
                        result,

                    "message":
                        message,
                }
            )


        runtime = health[
            "runtime"
        ]

        engine_status = (
            runtime[
                "engine"
            ][
                "status"
            ]
        )


        if engine_status == STATUS_ONLINE:

            add(
                "engine",
                "PhoenixEngine",
                PASS,
                "Moteur Phoenix Vision AI actif.",
            )

        elif engine_status == STATUS_AVAILABLE:

            add(
                "engine",
                "PhoenixEngine",
                WARNING,
                "Moteur disponible mais non actif.",
            )

        else:

            add(
                "engine",
                "PhoenixEngine",
                FAIL,
                "Moteur indisponible.",
            )


        stream_status = (
            runtime[
                "stream_service"
            ][
                "status"
            ]
        )


        if stream_status == STATUS_ONLINE:

            add(
                "stream",
                "Stream Service",
                PASS,
                "Service de diffusion actif.",
            )

        elif stream_status == STATUS_AVAILABLE:

            add(
                "stream",
                "Stream Service",
                WARNING,
                "Service disponible mais non actif.",
            )

        else:

            add(
                "stream",
                "Stream Service",
                FAIL,
                "Service de diffusion indisponible.",
            )


        databases = health[
            "databases"
        ]

        if databases[
            "unavailable"
        ] == 0:

            add(
                "databases",
                "Bases Phoenix Vision AI",
                PASS,
                (
                    f"{databases['online']}/"
                    f"{databases['count']} "
                    "bases accessibles."
                ),
            )

        else:

            add(
                "databases",
                "Bases Phoenix Vision AI",
                FAIL,
                (
                    f"{databases['unavailable']} "
                    "base(s) indisponible(s)."
                ),
            )


        memory_percent = (
            health[
                "machine"
            ][
                "memory"
            ][
                "percent"
            ]
        )

        if memory_percent >= 95:

            memory_result = FAIL

        elif memory_percent >= 90:

            memory_result = WARNING

        else:

            memory_result = PASS


        add(
            "memory",
            "Mémoire système",
            memory_result,
            (
                f"Utilisation mémoire : "
                f"{memory_percent}%."
            ),
        )


        disk_percent = (
            health[
                "machine"
            ][
                "disk"
            ][
                "percent"
            ]
        )

        if disk_percent >= 97:

            disk_result = FAIL

        elif disk_percent >= 90:

            disk_result = WARNING

        else:

            disk_result = PASS


        add(
            "disk",
            "Stockage système",
            disk_result,
            (
                f"Utilisation disque : "
                f"{disk_percent}%."
            ),
        )


        for (
            name,
            directory,
        ) in (
            health[
                "directories"
            ]
            .items()
        ):

            add(
                f"directory_{name}",
                f"Répertoire {name}",
                (
                    PASS
                    if directory[
                        "status"
                    ]
                    != STATUS_UNAVAILABLE
                    else FAIL
                ),
                (
                    "Répertoire accessible."
                    if directory[
                        "status"
                    ]
                    != STATUS_UNAVAILABLE
                    else
                    "Répertoire absent."
                ),
            )


        failed = sum(
            1
            for check
            in checks
            if check[
                "result"
            ] == FAIL
        )

        warnings = sum(
            1
            for check
            in checks
            if check[
                "result"
            ] == WARNING
        )


        if failed:

            result = FAIL

        elif warnings:

            result = WARNING

        else:

            result = PASS


        response = {
            "success":
                True,

            "diagnostic":
                "GENERAL",

            "result":
                result,

            "generated_at":
                utc_now_iso(),

            "checks":
                checks,

            "summary": {
                "total":
                    len(
                        checks
                    ),

                "ok":
                    sum(
                        1
                        for check
                        in checks
                        if check[
                            "result"
                        ] == PASS
                    ),

                "warnings":
                    warnings,

                "failed":
                    failed,
            },
        }


        self.record_event(
            action=
                "SYSTEM_DIAGNOSTIC_RUN",

            actor=
                actor,

            result=
                result,

            details={
                "summary":
                    response[
                        "summary"
                    ]
            },
        )


        return response


    # ========================================================
    # SQLITE QUICK CHECK
    # ========================================================

    def _database_path(
        self,
        database_name,
    ):

        raw_name = str(
            database_name
            or
            ""
        ).strip()


        if not raw_name:

            raise ValueError(
                "Nom de base invalide."
            )


        # Aucun chemin n'est accepté ici.
        # L'API reçoit uniquement un nom de fichier SQLite.
        if (
            raw_name
            !=
            Path(
                raw_name
            ).name
            or
            "/"
            in
            raw_name
            or
            "\\"
            in
            raw_name
        ):

            raise ValueError(
                "Nom de base invalide."
            )


        if not raw_name.endswith(
            ".db"
        ):

            raise ValueError(
                "Nom de base invalide."
            )


        data_root = (
            self.data_directory
            .resolve()
        )

        path = (
            data_root
            /
            raw_name
        ).resolve()


        # Protection supplémentaire notamment
        # contre un éventuel lien symbolique externe.
        if (
            path.parent
            !=
            data_root
        ):

            raise ValueError(
                "Chemin de base invalide."
            )


        known_databases = {
            candidate.name
            for candidate
            in data_root.glob(
                "*.db"
            )
            if candidate.is_file()
        }


        if (
            raw_name
            not in
            known_databases
        ):

            raise FileNotFoundError(
                raw_name
            )


        return path


    def _quick_check_database(
        self,
        path,
    ):

        uri = (
            "file:"
            +
            str(
                path
            )
            +
            "?mode=ro"
        )


        try:

            connection = sqlite3.connect(
                uri,
                uri=True,
                timeout=2.0,
            )


            try:

                rows = (
                    connection.execute(
                        "PRAGMA quick_check"
                    )
                    .fetchall()
                )

            finally:

                connection.close()


            messages = [
                str(
                    row[
                        0
                    ]
                )
                for row
                in rows
            ]


            valid = (
                len(
                    messages
                ) == 1
                and
                messages[
                    0
                ].lower()
                ==
                "ok"
            )


            return {
                "database":
                    path.name,

                "result":
                    (
                        PASS
                        if valid
                        else FAIL
                    ),

                "integrity":
                    (
                        "OK"
                        if valid
                        else
                        "ANOMALIE"
                    ),

                "messages":
                    messages[
                        :10
                    ],
            }


        except sqlite3.Error as error:

            return {
                "database":
                    path.name,

                "result":
                    FAIL,

                "integrity":
                    "ERREUR",

                "messages": [
                    type(
                        error
                    ).__name__
                ],
            }


    def quick_check(
        self,
        *,
        actor,
        database_name=None,
    ):

        if database_name:

            paths = [
                self._database_path(
                    database_name
                )
            ]

        else:

            paths = sorted(
                self.data_directory.glob(
                    "*.db"
                )
            )


        results = [
            self._quick_check_database(
                path
            )
            for path
            in paths
        ]


        failed = sum(
            1
            for item
            in results
            if item[
                "result"
            ] == FAIL
        )


        overall = (
            PASS
            if failed == 0
            else FAIL
        )


        response = {
            "success":
                True,

            "diagnostic":
                "SQLITE_QUICK_CHECK",

            "result":
                overall,

            "generated_at":
                utc_now_iso(),

            "checked":
                len(
                    results
                ),

            "failed":
                failed,

            "databases":
                results,
        }


        self.record_event(
            action=
                "DATABASE_QUICK_CHECK",

            actor=
                actor,

            target=
                (
                    database_name
                    or
                    "ALL_DATABASES"
                ),

            result=
                overall,

            details={
                "checked":
                    len(
                        results
                    ),

                "failed":
                    failed,
            },
        )


        return response


    # ========================================================
    # JOURNAL
    # ========================================================

    def recent_events(
        self,
        limit=50,
    ):

        limit = max(
            1,
            min(
                int(
                    limit
                ),
                200,
            ),
        )


        with self._connect_audit() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    action,
                    actor,
                    target,
                    result,
                    details_json,
                    created_at,
                    previous_hash,
                    event_hash
                FROM system_diagnostic_audit
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    limit,
                ),
            ).fetchall()


        return [
            {
                "id":
                    row[
                        "id"
                    ],

                "action":
                    row[
                        "action"
                    ],

                "actor":
                    row[
                        "actor"
                    ],

                "target":
                    row[
                        "target"
                    ],

                "result":
                    row[
                        "result"
                    ],

                "details":
                    json.loads(
                        row[
                            "details_json"
                        ]
                    ),

                "created_at":
                    row[
                        "created_at"
                    ],

                "event_hash":
                    row[
                        "event_hash"
                    ],
            }
            for row
            in rows
        ]


    def verify_audit_chain(
        self,
    ):

        with self._connect_audit() as connection:

            rows = connection.execute(
                """
                SELECT *
                FROM system_diagnostic_audit
                ORDER BY id ASC
                """
            ).fetchall()


        previous_hash = "GENESIS"


        for row in rows:

            details = json.loads(
                row[
                    "details_json"
                ]
            )

            payload = {
                "action":
                    row[
                        "action"
                    ],

                "actor":
                    row[
                        "actor"
                    ],

                "target":
                    row[
                        "target"
                    ],

                "result":
                    row[
                        "result"
                    ],

                "details":
                    details,

                "created_at":
                    row[
                        "created_at"
                    ],

                "previous_hash":
                    row[
                        "previous_hash"
                    ],
            }


            if (
                row[
                    "previous_hash"
                ]
                !=
                previous_hash
            ):

                return False


            canonical = json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(
                    ",",
                    ":",
                ),
            )

            calculated = (
                hashlib.sha256(
                    canonical.encode(
                        "utf-8"
                    )
                )
                .hexdigest()
            )


            if (
                calculated
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


system_diagnostics_service = (
    SystemDiagnosticsService()
)
