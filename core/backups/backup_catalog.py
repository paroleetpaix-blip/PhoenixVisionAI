"""
============================================================
PHOENIX VISION AI

Enterprise Backup Catalog

Phoenix Security Technologies
============================================================
"""

import json
import re

from pathlib import Path

from core.backups.backup_manifest import (
    verify_manifest_hash,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
)

from core.backups.backup_verifier import (
    backup_verifier,
)


BACKUP_ID_PATTERN = re.compile(
    r"^PHX-BKP-\d{8}-\d{6}-[A-F0-9]{6}$"
)


class BackupCatalog:

    def __init__(
        self,
        backup_directory=BACKUP_DIRECTORY,
    ):

        self.backup_directory = Path(
            backup_directory
        )


    # ========================================================
    # IDENTIFIER
    # ========================================================

    def _validate_backup_id(
        self,
        backup_id,
    ):

        backup_id = str(
            backup_id
            or
            ""
        ).strip()


        if not BACKUP_ID_PATTERN.fullmatch(
            backup_id
        ):

            raise ValueError(
                "Référence de sauvegarde invalide."
            )


        return backup_id


    # ========================================================
    # DIRECTORY
    # ========================================================

    def _backup_path(
        self,
        backup_id,
    ):

        backup_id = (
            self._validate_backup_id(
                backup_id
            )
        )

        root = (
            self.backup_directory
            .resolve()
        )

        path = (
            root
            /
            backup_id
        ).resolve()


        if path.parent != root:

            raise ValueError(
                "Chemin de sauvegarde invalide."
            )


        if (
            not path.is_dir()
            or
            path.is_symlink()
        ):

            raise FileNotFoundError(
                backup_id
            )


        return path


    # ========================================================
    # MANIFEST
    # ========================================================

    def _read_manifest_summary(
        self,
        backup_path,
    ):

        manifest_path = (
            backup_path
            /
            "manifest.json"
        )


        if not manifest_path.is_file():

            return {
                "backup_id":
                    backup_path.name,

                "status":
                    "INVALID",

                "manifest_valid":
                    False,

                "error":
                    "MANIFEST_MISSING",
            }


        manifest_valid = (
            verify_manifest_hash(
                backup_path
            )
        )


        try:

            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return {
                "backup_id":
                    backup_path.name,

                "status":
                    "INVALID",

                "manifest_valid":
                    False,

                "error":
                    "MANIFEST_JSON_INVALID",
            }


        manifest_backup_id = str(
            manifest.get(
                "backup_id"
            )
            or
            ""
        )


        identity_valid = (
            manifest_backup_id
            ==
            backup_path.name
        )


        valid = (
            manifest_valid
            and
            identity_valid
        )


        return {
            "backup_id":
                backup_path.name,

            "created_at":
                manifest.get(
                    "created_at"
                ),

            "application":
                manifest.get(
                    "application"
                ),

            "application_version":
                manifest.get(
                    "application_version"
                ),

            "backup_type":
                manifest.get(
                    "backup_type"
                ),

            "actor":
                manifest.get(
                    "actor"
                ),

            "file_count":
                manifest.get(
                    "file_count",
                    0,
                ),

            "total_size_bytes":
                manifest.get(
                    "total_size_bytes",
                    0,
                ),

            "category_counts":
                manifest.get(
                    "category_counts",
                    {},
                ),

            "manifest_valid":
                manifest_valid,

            "identity_valid":
                identity_valid,

            "status":
                (
                    "AVAILABLE"
                    if valid
                    else
                    "INVALID"
                ),
        }


    # ========================================================
    # LIST
    # ========================================================

    def list_backups(
        self,
        limit=100,
    ):

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError,
        ):

            limit = 100


        limit = max(
            1,
            min(
                limit,
                500,
            ),
        )


        if not self.backup_directory.is_dir():

            return []


        entries = []


        for path in (
            self.backup_directory
            .iterdir()
        ):

            if (
                not path.is_dir()
                or
                path.is_symlink()
            ):

                continue


            if (
                path.name.startswith(
                    "."
                )
            ):

                continue


            if not BACKUP_ID_PATTERN.fullmatch(
                path.name
            ):

                continue


            entries.append(
                self._read_manifest_summary(
                    path
                )
            )


        entries.sort(
            key=lambda item: str(
                item.get(
                    "created_at"
                )
                or
                ""
            ),
            reverse=True,
        )


        return entries[
            :limit
        ]


    # ========================================================
    # GET
    # ========================================================

    def get_backup(
        self,
        backup_id,
        *,
        verify_files=False,
    ):

        path = (
            self._backup_path(
                backup_id
            )
        )


        summary = (
            self._read_manifest_summary(
                path
            )
        )


        if verify_files:

            summary[
                "verification"
            ] = (
                backup_verifier
                .verify(
                    path
                )
            )


        return summary


    # ========================================================
    # LATEST
    # ========================================================

    def latest_backup(
        self,
    ):

        backups = (
            self.list_backups(
                limit=1
            )
        )


        if not backups:

            return None


        return backups[0]


    # ========================================================
    # STATS
    # ========================================================

    def statistics(
        self,
    ):

        backups = (
            self.list_backups(
                limit=500
            )
        )


        total_size = sum(
            int(
                backup.get(
                    "total_size_bytes",
                    0,
                )
                or
                0
            )

            for backup
            in backups
        )


        valid_count = sum(
            backup.get(
                "status"
            )
            ==
            "AVAILABLE"

            for backup
            in backups
        )


        invalid_count = (
            len(
                backups
            )
            -
            valid_count
        )


        return {
            "backup_count":
                len(
                    backups
                ),

            "available_count":
                valid_count,

            "invalid_count":
                invalid_count,

            "total_size_bytes":
                total_size,

            "latest":
                (
                    backups[0]
                    if backups
                    else None
                ),
        }


backup_catalog = BackupCatalog()
