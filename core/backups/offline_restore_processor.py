"""
============================================================
PHOENIX VISION AI

Offline Restore Processor

Phoenix Security Technologies
============================================================

Ce processeur permet de tester la restauration et le rollback
dans un environnement isolé.

Par sécurité, le projet Phoenix réel est interdit comme cible.
"""

import json
import os
import shutil
import sqlite3

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)

from core.backups.backup_policy import (
    PROJECT_ROOT,
    USER_IMAGE_EXTENSIONS,
)

from core.backups.backup_verifier import (
    backup_verifier,
)


CONFIGURATION_TARGETS = {
    "configuration/cameras.json":
        Path("data/cameras.json"),

    "configuration/config.json":
        Path("data/config.json"),

    "configuration/workspaces.json":
        Path("data/workspaces.json"),
}


SENSITIVE_TARGETS = {
    "sensitive/approved_users.json":
        Path("data/approved_users.json"),

    "sensitive/account_requests.json":
        Path("data/account_requests.json"),
}


class OfflineRestoreProcessor:

    # ========================================================
    # SAFETY
    # ========================================================

    def _validate_target_root(
        self,
        target_root,
    ):

        target_root = Path(
            target_root
        ).resolve()

        project_root = (
            PROJECT_ROOT
            .resolve()
        )


        if target_root == project_root:

            raise RuntimeError(
                "La restauration LIVE est interdite "
                "dans le processeur sandbox."
            )


        try:

            project_root.relative_to(
                target_root
            )

        except ValueError:

            pass

        else:

            raise RuntimeError(
                "La cible sandbox ne peut pas "
                "englober le projet Phoenix."
            )


        return target_root


    # ========================================================
    # BACKUP
    # ========================================================

    def _load_verified_manifest(
        self,
        backup_directory,
    ):

        backup_directory = Path(
            backup_directory
        ).resolve()


        if (
            not backup_directory.is_dir()
            or
            backup_directory.is_symlink()
        ):

            raise FileNotFoundError(
                backup_directory
            )


        verification = (
            backup_verifier
            .verify(
                backup_directory
            )
        )


        if not verification.get(
            "success"
        ):

            raise RuntimeError(
                "Sauvegarde invalide : "
                +
                str(
                    verification.get(
                        "status"
                    )
                )
            )


        manifest_path = (
            backup_directory
            /
            "manifest.json"
        )


        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )


        if (
            manifest.get(
                "backup_id"
            )
            !=
            backup_directory.name
        ):

            raise RuntimeError(
                "Identité du backup incohérente."
            )


        return (
            backup_directory,
            manifest,
        )


    # ========================================================
    # TARGET MAPPING
    # ========================================================

    def _relative_target(
        self,
        entry,
    ):

        archive_path = str(
            entry.get(
                "archive_path"
            )
            or
            ""
        ).strip()

        category = str(
            entry.get(
                "category"
            )
            or
            ""
        ).strip()


        relative = Path(
            archive_path
        )


        if (
            not archive_path
            or
            relative.is_absolute()
            or
            ".."
            in
            relative.parts
        ):

            raise ValueError(
                "Chemin d'archive invalide."
            )


        if category == "DATABASE":

            if (
                len(
                    relative.parts
                )
                !=
                2
                or
                relative.parts[0]
                !=
                "databases"
            ):

                raise ValueError(
                    "Chemin de base invalide."
                )


            name = (
                relative.parts[1]
            )


            if (
                Path(
                    name
                ).name
                !=
                name
                or
                not name.endswith(
                    ".db"
                )
            ):

                raise ValueError(
                    "Nom de base invalide."
                )


            if (
                name
                ==
                "vehicle_history.db"
            ):

                return Path(
                    "database/"
                    "vehicle_history.db"
                )


            return (
                Path("data")
                /
                name
            )


        if category == "CONFIGURATION":

            target = (
                CONFIGURATION_TARGETS
                .get(
                    archive_path
                )
            )


            if target is None:

                raise ValueError(
                    "Configuration interdite."
                )


            return target


        if category == "SENSITIVE_AUTH":

            target = (
                SENSITIVE_TARGETS
                .get(
                    archive_path
                )
            )


            if target is None:

                raise ValueError(
                    "Fichier sensible interdit."
                )


            return target


        if (
            category
            ==
            "SENSITIVE_USER_ASSET"
        ):

            parts = (
                relative.parts
            )


            if (
                len(
                    parts
                )
                <
                3
                or
                parts[0]
                !=
                "sensitive"
                or
                parts[1]
                !=
                "user_photos"
            ):

                raise ValueError(
                    "Chemin photo invalide."
                )


            photo_relative = Path(
                *parts[
                    2:
                ]
            )


            if (
                photo_relative.suffix.lower()
                not in
                USER_IMAGE_EXTENSIONS
            ):

                raise ValueError(
                    "Format photo interdit."
                )


            return (
                Path(
                    "web/static/uploads/users"
                )
                /
                photo_relative
            )


        raise ValueError(
            "Catégorie de restauration interdite."
        )


    # ========================================================
    # FILE OPERATIONS
    # ========================================================

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


    def _remove_sqlite_sidecars(
        self,
        database_path,
    ):

        database_path = Path(
            database_path
        )


        for suffix in (
            "-wal",
            "-shm",
        ):

            sidecar = Path(
                str(
                    database_path
                )
                +
                suffix
            )


            if (
                sidecar.exists()
                and
                not sidecar.is_symlink()
            ):

                sidecar.unlink()


    def _atomic_copy(
        self,
        source,
        target,
        *,
        database=False,
    ):

        source = Path(
            source
        )

        target = Path(
            target
        )


        self._secure_directory(
            target.parent
        )


        temporary = (
            target.parent
            /
            (
                "."
                +
                target.name
                +
                ".phoenix-restore.tmp"
            )
        )


        if temporary.exists():

            temporary.unlink()


        shutil.copy2(
            source,
            temporary,
        )

        os.chmod(
            temporary,
            0o600,
        )


        if database:

            self._remove_sqlite_sidecars(
                target
            )


        os.replace(
            temporary,
            target,
        )

        os.chmod(
            target,
            0o600,
        )


        if database:

            self._remove_sqlite_sidecars(
                target
            )


    # ========================================================
    # APPLY
    # ========================================================

    def _apply(
        self,
        backup_directory,
        manifest,
        target_root,
        *,
        simulate_failure_after=None,
    ):

        target_root = (
            self._validate_target_root(
                target_root
            )
        )


        files = manifest.get(
            "files"
        )


        if not isinstance(
            files,
            list,
        ):

            raise RuntimeError(
                "Manifest sans liste de fichiers."
            )


        written = 0


        for entry in files:

            archive_path = str(
                entry[
                    "archive_path"
                ]
            )


            source = (
                backup_directory
                /
                archive_path
            ).resolve()


            try:

                source.relative_to(
                    backup_directory.resolve()
                )

            except ValueError:

                raise RuntimeError(
                    "Source hors sauvegarde."
                )


            if (
                not source.is_file()
                or
                source.is_symlink()
            ):

                raise RuntimeError(
                    "Source de restauration invalide."
                )


            relative_target = (
                self._relative_target(
                    entry
                )
            )


            target = (
                target_root
                /
                relative_target
            ).resolve()


            try:

                target.relative_to(
                    target_root
                )

            except ValueError:

                raise RuntimeError(
                    "Destination hors sandbox."
                )


            is_database = (
                entry.get(
                    "category"
                )
                ==
                "DATABASE"
            )


            self._atomic_copy(
                source,
                target,
                database=
                    is_database,
            )


            written += 1


            if (
                simulate_failure_after
                is not None
                and
                written
                >=
                int(
                    simulate_failure_after
                )
            ):

                raise RuntimeError(
                    "SIMULATED_RESTORE_FAILURE"
                )


        return written


    # ========================================================
    # VERIFY TARGET
    # ========================================================

    def verify_target(
        self,
        manifest,
        target_root,
    ):

        target_root = (
            self._validate_target_root(
                target_root
            )
        )


        checked = 0
        valid = 0

        databases_checked = 0
        databases_valid = 0

        details = []


        for entry in manifest.get(
            "files",
            []
        ):

            relative_target = (
                self._relative_target(
                    entry
                )
            )


            target = (
                target_root
                /
                relative_target
            ).resolve()


            checked += 1


            if not target.is_file():

                details.append(
                    {
                        "path":
                            str(
                                relative_target
                            ),

                        "status":
                            "MISSING",
                    }
                )

                continue


            expected_size = int(
                entry.get(
                    "size_bytes",
                    -1,
                )
            )

            expected_hash = str(
                entry.get(
                    "sha256"
                )
                or
                ""
            ).lower()


            size_valid = (
                target.stat().st_size
                ==
                expected_size
            )

            hash_valid = (
                sha256_file(
                    target
                )
                ==
                expected_hash
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


                    sqlite_valid = (
                        bool(
                            rows
                        )
                        and
                        all(
                            str(
                                row[0]
                            ).lower()
                            ==
                            "ok"

                            for row
                            in rows
                        )
                    )


                except sqlite3.Error:

                    sqlite_valid = False


                if sqlite_valid:

                    databases_valid += 1


            item_valid = (
                size_valid
                and
                hash_valid
                and
                sqlite_valid
                is not False
            )


            if item_valid:

                valid += 1


            details.append(
                {
                    "path":
                        str(
                            relative_target
                        ),

                    "status":
                        (
                            "OK"
                            if item_valid
                            else
                            "INVALID"
                        ),

                    "size_valid":
                        size_valid,

                    "sha256_valid":
                        hash_valid,

                    "sqlite_valid":
                        sqlite_valid,
                }
            )


        return {
            "success":
                checked == valid,

            "status":
                (
                    "VALID"
                    if checked == valid
                    else
                    "INVALID"
                ),

            "files_checked":
                checked,

            "files_valid":
                valid,

            "databases_checked":
                databases_checked,

            "databases_valid":
                databases_valid,

            "details":
                details,
        }


    # ========================================================
    # SEED SANDBOX
    # ========================================================

    def seed_sandbox(
        self,
        backup_directory,
        target_root,
    ):

        backup_directory, manifest = (
            self._load_verified_manifest(
                backup_directory
            )
        )


        self._apply(
            backup_directory,
            manifest,
            target_root,
        )


        verification = (
            self.verify_target(
                manifest,
                target_root,
            )
        )


        if not verification.get(
            "success"
        ):

            raise RuntimeError(
                "Initialisation sandbox invalide."
            )


        return verification


    # ========================================================
    # RESTORE + ROLLBACK
    # ========================================================

    def restore_sandbox(
        self,
        *,
        backup_directory,
        pre_restore_backup_directory,
        target_root,
        simulate_failure_after=None,
        simulate_rollback_failure_after=None,
    ):

        backup_directory, manifest = (
            self._load_verified_manifest(
                backup_directory
            )
        )

        (
            pre_restore_backup_directory,
            pre_restore_manifest,
        ) = (
            self._load_verified_manifest(
                pre_restore_backup_directory
            )
        )


        if (
            manifest.get("application")
            !=
            pre_restore_manifest.get("application")
        ):

            raise RuntimeError(
                "Applications incompatibles."
            )


        if (
            manifest.get("application_version")
            !=
            pre_restore_manifest.get(
                "application_version"
            )
        ):

            raise RuntimeError(
                "Versions incompatibles."
            )


        try:

            written = self._apply(
                backup_directory,
                manifest,
                target_root,
                simulate_failure_after=
                    simulate_failure_after,
            )


            verification = self.verify_target(
                manifest,
                target_root,
            )


            if not verification.get(
                "success"
            ):

                raise RuntimeError(
                    "POST_RESTORE_VERIFY_FAILED"
                )


            return {
                "success": True,
                "status": "RESTORED",
                "backup_id":
                    manifest.get("backup_id"),
                "files_written": written,
                "verification": verification,
                "rollback_performed": False,
            }


        except Exception as restore_error:

            restore_error_text = str(
                restore_error
            )


        try:

            rollback_written = self._apply(
                pre_restore_backup_directory,
                pre_restore_manifest,
                target_root,
                simulate_failure_after=
                    simulate_rollback_failure_after,
            )


            rollback_verification = (
                self.verify_target(
                    pre_restore_manifest,
                    target_root,
                )
            )


            if not rollback_verification.get(
                "success"
            ):

                return {
                    "success": False,
                    "status": "ROLLBACK_FAILED",
                    "backup_id":
                        manifest.get("backup_id"),
                    "pre_restore_backup_id":
                        pre_restore_manifest.get(
                            "backup_id"
                        ),
                    "restore_error":
                        restore_error_text,
                    "rollback_error":
                        "ROLLBACK_VERIFY_FAILED",
                    "rollback_performed": True,
                    "rollback_files_written":
                        rollback_written,
                    "rollback_verification":
                        rollback_verification,
                }


            return {
                "success": False,
                "status": "ROLLED_BACK",
                "backup_id":
                    manifest.get("backup_id"),
                "pre_restore_backup_id":
                    pre_restore_manifest.get(
                        "backup_id"
                    ),
                "restore_error":
                    restore_error_text,
                "rollback_performed": True,
                "rollback_files_written":
                    rollback_written,
                "rollback_verification":
                    rollback_verification,
            }


        except Exception as rollback_error:

            return {
                "success": False,
                "status": "ROLLBACK_FAILED",
                "backup_id":
                    manifest.get("backup_id"),
                "pre_restore_backup_id":
                    pre_restore_manifest.get(
                        "backup_id"
                    ),
                "restore_error":
                    restore_error_text,
                "rollback_error":
                    str(rollback_error),
                "rollback_performed": True,
                "rollback_files_written": None,
                "rollback_verification": {
                    "success": False,
                    "status": "INVALID",
                    "files_checked": 0,
                    "files_valid": 0,
                    "databases_checked": 0,
                    "databases_valid": 0,
                },
            }


offline_restore_processor = (
    OfflineRestoreProcessor()
)
