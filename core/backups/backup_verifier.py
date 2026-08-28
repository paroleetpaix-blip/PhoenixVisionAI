"""
============================================================
PHOENIX VISION AI

Enterprise Backup Verifier

Phoenix Security Technologies
============================================================
"""

import json
import sqlite3

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
    verify_manifest_hash,
)


class BackupVerifier:

    def verify(
        self,
        backup_directory,
    ):

        backup_directory = Path(
            backup_directory
        ).resolve()


        manifest_path = (
            backup_directory
            /
            "manifest.json"
        )


        if not manifest_path.is_file():

            return {
                "success": False,
                "status": "INVALID",
                "error": "MANIFEST_MISSING",
                "files_checked": 0,
                "files_valid": 0,
                "files_invalid": 0,
                "databases_checked": 0,
                "databases_valid": 0,
                "details": [],
            }


        if not verify_manifest_hash(
            backup_directory
        ):

            return {
                "success": False,
                "status": "INVALID",
                "error": "MANIFEST_HASH_INVALID",
                "files_checked": 0,
                "files_valid": 0,
                "files_invalid": 0,
                "databases_checked": 0,
                "databases_valid": 0,
                "details": [],
            }


        try:

            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return {
                "success": False,
                "status": "INVALID",
                "error": "MANIFEST_JSON_INVALID",
                "files_checked": 0,
                "files_valid": 0,
                "files_invalid": 0,
                "databases_checked": 0,
                "databases_valid": 0,
                "details": [],
            }


        files = manifest.get(
            "files",
            []
        )


        if not isinstance(
            files,
            list,
        ):

            return {
                "success": False,
                "status": "INVALID",
                "error": "MANIFEST_FILES_INVALID",
                "files_checked": 0,
                "files_valid": 0,
                "files_invalid": 0,
                "databases_checked": 0,
                "databases_valid": 0,
                "details": [],
            }


        details = []

        files_valid = 0
        files_invalid = 0

        databases_checked = 0
        databases_valid = 0


        for entry in files:

            archive_path = str(
                entry.get(
                    "archive_path"
                )
                or
                ""
            ).strip()


            relative_path = Path(
                archive_path
            )


            # Aucun chemin absolu ou sortant du backup.
            if (
                not archive_path
                or
                relative_path.is_absolute()
                or
                ".."
                in
                relative_path.parts
            ):

                details.append(
                    {
                        "archive_path":
                            archive_path,

                        "status":
                            "INVALID_PATH",
                    }
                )

                files_invalid += 1

                continue


            target = (
                backup_directory
                /
                relative_path
            ).resolve()


            try:

                target.relative_to(
                    backup_directory
                )

            except ValueError:

                details.append(
                    {
                        "archive_path":
                            archive_path,

                        "status":
                            "INVALID_PATH",
                    }
                )

                files_invalid += 1

                continue


            if (
                not target.is_file()
                or
                target.is_symlink()
            ):

                details.append(
                    {
                        "archive_path":
                            archive_path,

                        "status":
                            "MISSING",
                    }
                )

                files_invalid += 1

                continue


            expected_size = int(
                entry.get(
                    "size_bytes",
                    -1,
                )
            )

            actual_size = (
                target.stat()
                .st_size
            )


            expected_hash = str(
                entry.get(
                    "sha256"
                )
                or
                ""
            ).lower()

            actual_hash = sha256_file(
                target
            )


            size_valid = (
                expected_size
                ==
                actual_size
            )

            hash_valid = (
                bool(
                    expected_hash
                )
                and
                expected_hash
                ==
                actual_hash
            )


            sqlite_valid = None


            if (
                entry.get(
                    "category"
                )
                ==
                "DATABASE"
            ):

                databases_checked += 1


                uri = (
                    "file:"
                    +
                    str(
                        target
                    )
                    +
                    "?mode=ro"
                )


                try:

                    connection = (
                        sqlite3.connect(
                            uri,
                            uri=True,
                            timeout=2.0,
                        )
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
                            row[0]
                        ).lower()

                        for row
                        in rows
                    ]


                    sqlite_valid = (
                        bool(
                            messages
                        )
                        and
                        all(
                            message
                            ==
                            "ok"

                            for message
                            in messages
                        )
                    )


                except sqlite3.Error:

                    sqlite_valid = False


                if sqlite_valid:

                    databases_valid += 1


            valid = (
                size_valid
                and
                hash_valid
                and
                (
                    sqlite_valid
                    is not False
                )
            )


            if valid:

                files_valid += 1

            else:

                files_invalid += 1


            details.append(
                {
                    "archive_path":
                        archive_path,

                    "category":
                        entry.get(
                            "category"
                        ),

                    "status":
                        (
                            "OK"
                            if valid
                            else
                            "INVALID"
                        ),

                    "size_valid":
                        size_valid,

                    "sha256_valid":
                        hash_valid,

                    "sqlite_quick_check":
                        (
                            "OK"
                            if sqlite_valid is True
                            else
                            (
                                "FAILED"
                                if sqlite_valid is False
                                else
                                None
                            )
                        ),
                }
            )


        success = (
            files_invalid == 0
            and
            files_valid
            ==
            len(
                files
            )
        )


        return {
            "success":
                success,

            "status":
                (
                    "VALID"
                    if success
                    else
                    "INVALID"
                ),

            "backup_id":
                manifest.get(
                    "backup_id"
                ),

            "application":
                manifest.get(
                    "application"
                ),

            "application_version":
                manifest.get(
                    "application_version"
                ),

            "manifest_valid":
                True,

            "files_checked":
                len(
                    files
                ),

            "files_valid":
                files_valid,

            "files_invalid":
                files_invalid,

            "databases_checked":
                databases_checked,

            "databases_valid":
                databases_valid,

            "details":
                details,
        }


backup_verifier = BackupVerifier()
