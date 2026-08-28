"""
============================================================
PHOENIX VISION AI

Enterprise Backup Service

Phoenix Security Technologies
============================================================
"""

import os
import secrets
import shutil
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core.backups.backup_manifest import (
    build_manifest,
    project_relative_path,
    sha256_file,
    verify_manifest_hash,
    write_manifest,
)

from core.backups.backup_policy import (
    DATA_DIRECTORY,
    discover_backup_sources,
)


BACKUP_DIRECTORY = (
    DATA_DIRECTORY
    /
    "backups"
)


class BackupService:

    def __init__(
        self,
        backup_directory=BACKUP_DIRECTORY,
    ):

        self.backup_directory = Path(
            backup_directory
        )


    # ========================================================
    # FILESYSTEM SECURITY
    # ========================================================

    def _prepare_backup_root(
        self,
    ):

        if (
            self.backup_directory
            .exists()
            and
            self.backup_directory
            .is_symlink()
        ):

            raise RuntimeError(
                "Le dossier de sauvegarde "
                "ne peut pas être un lien symbolique."
            )


        self.backup_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            self.backup_directory,
            0o700,
        )


    def _secure_directory(
        self,
        path,
    ):

        path = Path(
            path
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            path,
            0o700,
        )


    def _secure_file(
        self,
        path,
    ):

        os.chmod(
            Path(
                path
            ),
            0o600,
        )


    # ========================================================
    # IDENTIFIER
    # ========================================================

    def _new_backup_id(
        self,
    ):

        timestamp = (
            datetime.now(
                timezone.utc
            )
            .strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        suffix = (
            secrets
            .token_hex(
                3
            )
            .upper()
        )


        return (
            "PHX-BKP-"
            +
            timestamp
            +
            "-"
            +
            suffix
        )


    # ========================================================
    # SQLITE
    # ========================================================

    def _backup_database(
        self,
        source_path,
        destination_path,
    ):

        source_path = Path(
            source_path
        ).resolve()

        destination_path = Path(
            destination_path
        )


        if not source_path.is_file():

            raise FileNotFoundError(
                source_path
            )


        self._secure_directory(
            destination_path.parent
        )


        source_uri = (
            "file:"
            +
            str(
                source_path
            )
            +
            "?mode=ro"
        )


        source_connection = None

        destination_connection = None


        try:

            source_connection = (
                sqlite3.connect(
                    source_uri,
                    uri=True,
                    timeout=5.0,
                )
            )

            destination_connection = (
                sqlite3.connect(
                    str(
                        destination_path
                    ),
                    timeout=5.0,
                )
            )


            source_connection.backup(
                destination_connection,
                pages=256,
                sleep=0.05,
            )


            destination_connection.commit()


            rows = (
                destination_connection
                .execute(
                    "PRAGMA quick_check"
                )
                .fetchall()
            )


            messages = [
                str(
                    row[0]
                )

                for row
                in rows
            ]


            valid = (
                bool(
                    messages
                )
                and
                all(
                    message.lower()
                    ==
                    "ok"

                    for message
                    in messages
                )
            )


            if not valid:

                raise RuntimeError(
                    "Échec du contrôle SQLite "
                    f"pour {source_path.name}: "
                    +
                    "; ".join(
                        messages
                    )
                )


        finally:

            if destination_connection is not None:

                destination_connection.close()


            if source_connection is not None:

                source_connection.close()


        self._secure_file(
            destination_path
        )


        return "OK"


    # ========================================================
    # STANDARD FILES
    # ========================================================

    def _copy_standard_file(
        self,
        source_path,
        destination_path,
    ):

        source_path = Path(
            source_path
        )

        destination_path = Path(
            destination_path
        )


        if not source_path.is_file():

            raise FileNotFoundError(
                source_path
            )


        if source_path.is_symlink():

            raise RuntimeError(
                "Les liens symboliques "
                "ne sont pas sauvegardés."
            )


        self._secure_directory(
            destination_path.parent
        )


        shutil.copy2(
            source_path,
            destination_path,
        )


        self._secure_file(
            destination_path
        )


    # ========================================================
    # CREATE BACKUP
    # ========================================================

    def create_backup(
        self,
        *,
        actor="LOCAL_ADMIN",
        backup_type="MANUAL",
    ):

        self._prepare_backup_root()


        sources = (
            discover_backup_sources()
        )


        if not sources:

            raise RuntimeError(
                "Aucune source de sauvegarde "
                "Phoenix disponible."
            )


        database_count = sum(
            source.category
            ==
            "DATABASE"

            for source
            in sources
        )


        if database_count == 0:

            raise RuntimeError(
                "Aucune base Phoenix "
                "à sauvegarder."
            )


        backup_id = (
            self._new_backup_id()
        )


        final_directory = (
            self.backup_directory
            /
            backup_id
        )


        partial_directory = (
            self.backup_directory
            /
            (
                "."
                +
                backup_id
                +
                ".partial"
            )
        )


        if (
            final_directory.exists()
            or
            partial_directory.exists()
        ):

            raise RuntimeError(
                "Collision d'identifiant "
                "de sauvegarde."
            )


        self._secure_directory(
            partial_directory
        )


        file_records = []


        try:

            for source in sources:

                destination = (
                    partial_directory
                    /
                    source.archive_path
                )


                if source.category == "DATABASE":

                    quick_check = (
                        self._backup_database(
                            source.source_path,
                            destination,
                        )
                    )

                else:

                    self._copy_standard_file(
                        source.source_path,
                        destination,
                    )

                    quick_check = None


                size_bytes = (
                    destination
                    .stat()
                    .st_size
                )


                digest = sha256_file(
                    destination
                )


                record = {
                    "source_path":
                        project_relative_path(
                            source.source_path
                        ),

                    "archive_path":
                        str(
                            source.archive_path
                        ),

                    "category":
                        source.category,

                    "sensitive":
                        bool(
                            source.sensitive
                        ),

                    "size_bytes":
                        size_bytes,

                    "sha256":
                        digest,
                }


                if quick_check is not None:

                    record[
                        "sqlite_quick_check"
                    ] = quick_check


                file_records.append(
                    record
                )


            manifest = build_manifest(
                backup_id=
                    backup_id,

                actor=
                    actor,

                backup_type=
                    backup_type,

                files=
                    file_records,
            )


            manifest_info = write_manifest(
                partial_directory,
                manifest,
            )


            if not verify_manifest_hash(
                partial_directory
            ):

                raise RuntimeError(
                    "Échec du contrôle "
                    "d'intégrité du manifest."
                )


            partial_directory.rename(
                final_directory
            )


            os.chmod(
                final_directory,
                0o700,
            )


            return {
                "success":
                    True,

                "backup_id":
                    backup_id,

                "backup_directory":
                    str(
                        final_directory
                    ),

                "backup_type":
                    str(
                        backup_type
                    ).upper(),

                "file_count":
                    manifest[
                        "file_count"
                    ],

                "total_size_bytes":
                    manifest[
                        "total_size_bytes"
                    ],

                "category_counts":
                    manifest[
                        "category_counts"
                    ],

                "manifest_sha256":
                    manifest_info[
                        "manifest_sha256"
                    ],

                "integrity":
                    True,
            }


        except Exception:

            if partial_directory.exists():

                shutil.rmtree(
                    partial_directory,
                    ignore_errors=True,
                )


            raise


backup_service = BackupService()
