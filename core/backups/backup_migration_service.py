"""
============================================================
PHOENIX VISION AI

Backup Migration Service

Phoenix Security Technologies
============================================================

Prépare et contrôle la migration de sauvegardes Phoenix.

IMPORTANT
---------
Le backup original n'est jamais modifié.
"""

import hashlib
import json
import os
import secrets
import shutil
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core import constants

from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_manifest import (
    build_manifest,
    sha256_file,
    verify_manifest_hash,
    write_manifest,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
    backup_service,
)

from core.backups.backup_migration_registry import (
    backup_migration_registry,
)

from core.backups.restore_request import (
    validate_backup_id,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MIGRATION_WORK_ROOT = (
    PROJECT_ROOT
    /
    "data"
    /
    ".backup-migrations"
)


class BackupMigrationService:

    def __init__(
        self,
        *,
        catalog=backup_catalog,
        registry=backup_migration_registry,
        work_root=MIGRATION_WORK_ROOT,
        backup_root=BACKUP_DIRECTORY,
    ):

        self.catalog = catalog

        self.registry = registry

        self.work_root = Path(
            work_root
        )

        self.backup_root = Path(
            backup_root
        )


    # ========================================================
    # BACKUP DIRECTORY
    # ========================================================

    def _backup_directory(
        self,
        backup_id,
    ):

        backup_id = (
            validate_backup_id(
                backup_id
            )
        )


        root = (
            self.backup_root
            .resolve()
        )

        directory = (
            root
            /
            backup_id
        ).resolve()


        if directory.parent != root:

            raise RuntimeError(
                "Chemin backup migration invalide."
            )


        if (
            not directory.is_dir()
            or
            directory.is_symlink()
        ):

            raise FileNotFoundError(
                backup_id
            )


        return directory


    # ========================================================
    # MANIFEST
    # ========================================================

    @staticmethod
    def _read_manifest(
        backup_directory,
    ):

        path = (
            Path(
                backup_directory
            )
            /
            "manifest.json"
        )


        if (
            not path.is_file()
            or
            path.is_symlink()
        ):

            raise RuntimeError(
                "Manifest migration invalide."
            )


        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            payload,
            dict,
        ):

            raise RuntimeError(
                "Manifest migration invalide."
            )


        return payload


    # ========================================================
    # PREFLIGHT
    # ========================================================

    def preflight(
        self,
        backup_id,
    ):

        backup_id = (
            validate_backup_id(
                backup_id
            )
        )


        backup = (
            self.catalog
            .get_backup(
                backup_id,
                verify_files=True,
            )
        )


        if (
            backup.get(
                "status"
            )
            !=
            "AVAILABLE"
        ):

            raise RuntimeError(
                "Backup indisponible."
            )


        verification = (
            backup.get(
                "verification"
            )
            or
            {}
        )


        if not verification.get(
            "success"
        ):

            raise RuntimeError(
                "Backup source invalide."
            )


        current_application = getattr(
            constants,
            "APP_NAME",
            "Phoenix Vision AI",
        )

        current_version = getattr(
            constants,
            "VERSION",
            "unknown",
        )


        source_application = backup.get(
            "application"
        )

        source_version = backup.get(
            "application_version"
        )


        if source_application != current_application:

            raise RuntimeError(
                "Application backup incompatible."
            )


        if not source_version:

            raise RuntimeError(
                "Version source absente."
            )


        # ====================================================
        # SAME VERSION
        # ====================================================

        if source_version == current_version:

            return {
                "success":
                    True,

                "status":
                    "MIGRATION_NOT_REQUIRED",

                "backup_id":
                    backup_id,

                "source_version":
                    source_version,

                "target_version":
                    current_version,

                "chain":
                    [],

                "original_backup_modified":
                    False,
            }


        # ====================================================
        # MIGRATION CHAIN
        # ====================================================

        chain = (
            self.registry
            .find_chain(
                source_version=
                    source_version,

                target_version=
                    current_version,
            )
        )


        if chain is None:

            return {
                "success":
                    False,

                "status":
                    "MIGRATION_PATH_NOT_FOUND",

                "backup_id":
                    backup_id,

                "source_version":
                    source_version,

                "target_version":
                    current_version,

                "chain":
                    None,

                "original_backup_modified":
                    False,
            }


        return {
            "success":
                True,

            "status":
                "MIGRATION_READY",

            "backup_id":
                backup_id,

            "source_version":
                source_version,

            "target_version":
                current_version,

            "chain":
                [
                    {
                        "source_version":
                            step[
                                "source_version"
                            ],

                        "target_version":
                            step[
                                "target_version"
                            ],
                    }

                    for step
                    in chain
                ],

            "original_backup_modified":
                False,
        }


    # ========================================================
    # PREPARE WORK COPY
    # ========================================================

    def prepare_work_copy(
        self,
        backup_id,
    ):

        preflight = self.preflight(
            backup_id
        )


        if preflight[
            "status"
        ] == "MIGRATION_NOT_REQUIRED":

            return {
                **preflight,

                "work_copy_created":
                    False,
            }


        if not preflight[
            "success"
        ]:

            return {
                **preflight,

                "work_copy_created":
                    False,
            }


        source = (
            self._backup_directory(
                backup_id
            )
        )


        self.work_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            self.work_root,
            0o700,
        )


        work_directory = (
            self.work_root
            /
            (
                backup_id
                +
                "__"
                +
                preflight[
                    "target_version"
                ]
                .replace(
                    "/",
                    "_"
                )
            )
        )


        if (
            work_directory.exists()
            or
            work_directory.is_symlink()
        ):

            raise RuntimeError(
                "Copie de migration déjà présente."
            )


        shutil.copytree(
            source,
            work_directory,
            symlinks=False,
        )


        os.chmod(
            work_directory,
            0o700,
        )


        for item in work_directory.rglob(
            "*"
        ):

            if item.is_symlink():

                shutil.rmtree(
                    work_directory,
                    ignore_errors=True,
                )

                raise RuntimeError(
                    "Lien symbolique détecté "
                    "dans la copie de migration."
                )


            if item.is_file():

                os.chmod(
                    item,
                    0o600,
                )


            elif item.is_dir():

                os.chmod(
                    item,
                    0o700,
                )


        return {
            **preflight,

            "work_copy_created":
                True,

            "work_directory":
                str(
                    work_directory
                ),

            "original_backup_modified":
                False,
        }

    # ========================================================
    # UTC
    # ========================================================

    @staticmethod
    def _utc_now_iso(
        self=None,
    ):

        return (
            datetime.now(
                timezone.utc
            )
            .replace(
                microsecond=0
            )
            .isoformat()
        )


    # ========================================================
    # FSYNC DIRECTORY
    # ========================================================

    @staticmethod
    def _fsync_directory(
        path,
    ):

        path = Path(
            path
        )


        flags = os.O_RDONLY

        if hasattr(
            os,
            "O_DIRECTORY",
        ):

            flags |= os.O_DIRECTORY


        try:

            descriptor = os.open(
                str(
                    path
                ),
                flags,
            )

        except OSError:

            return


        try:

            os.fsync(
                descriptor
            )

        finally:

            os.close(
                descriptor
            )


    # ========================================================
    # ATOMIC JSON
    # ========================================================

    def _atomic_json_write(
        self,
        path,
        payload,
    ):

        path = Path(
            path
        )


        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            path.parent,
            0o700,
        )


        if path.is_symlink():

            raise RuntimeError(
                "Fichier migration symbolique interdit."
            )


        temporary = (
            path.parent
            /
            (
                "."
                +
                path.name
                +
                "."
                +
                secrets.token_hex(
                    4
                )
                +
                ".tmp"
            )
        )


        try:

            with temporary.open(
                "x",
                encoding="utf-8",
            ) as handle:

                json.dump(
                    payload,
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )

                handle.write(
                    "\n"
                )

                handle.flush()

                os.fsync(
                    handle.fileno()
                )


            os.chmod(
                temporary,
                0o600,
            )

            os.replace(
                temporary,
                path,
            )

            os.chmod(
                path,
                0o600,
            )

            self._fsync_directory(
                path.parent
            )


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    # ========================================================
    # TREE FINGERPRINT
    # ========================================================

    @staticmethod
    def _tree_fingerprint(
        directory,
    ):

        directory = Path(
            directory
        ).resolve()


        if (
            not directory.is_dir()
            or
            directory.is_symlink()
        ):

            raise RuntimeError(
                "Répertoire fingerprint invalide."
            )


        digest = hashlib.sha256()


        files = sorted(
            (
                item
                for item
                in directory.rglob("*")
                if item.is_file()
            ),
            key=lambda item:
                str(
                    item.relative_to(
                        directory
                    )
                ),
        )


        for item in files:

            if item.is_symlink():

                raise RuntimeError(
                    "Lien symbolique interdit "
                    "dans le backup."
                )


            relative = str(
                item.relative_to(
                    directory
                )
            )


            digest.update(
                relative.encode(
                    "utf-8"
                )
            )

            digest.update(
                b"\0"
            )


            file_digest = hashlib.sha256()


            with item.open(
                "rb"
            ) as handle:

                while True:

                    block = handle.read(
                        1024
                        *
                        1024
                    )

                    if not block:

                        break

                    file_digest.update(
                        block
                    )


            digest.update(
                file_digest.digest()
            )


        return digest.hexdigest()


    # ========================================================
    # SQLITE QUICK CHECK
    # ========================================================

    @staticmethod
    def _sqlite_quick_check(
        path,
    ):

        path = Path(
            path
        ).resolve()


        connection = sqlite3.connect(
            "file:"
            +
            str(
                path
            )
            +
            "?mode=ro",
            uri=True,
        )


        try:

            row = connection.execute(
                "PRAGMA quick_check"
            ).fetchone()

        finally:

            connection.close()


        return bool(
            row
            and
            str(
                row[0]
            ).lower()
            ==
            "ok"
        )


    # ========================================================
    # WORK COPY VALIDATION
    # ========================================================

    def _validate_work_copy(
        self,
        work_directory,
    ):

        work_directory = Path(
            work_directory
        ).resolve()


        if (
            not work_directory.is_dir()
            or
            work_directory.is_symlink()
        ):

            raise RuntimeError(
                "Copie de migration invalide."
            )


        files_checked = 0

        databases_checked = 0

        databases_valid = 0


        for item in work_directory.rglob(
            "*"
        ):

            if item.is_symlink():

                raise RuntimeError(
                    "Lien symbolique interdit "
                    "dans la migration."
                )


            if not item.is_file():

                continue


            files_checked += 1


            if item.suffix.lower() == ".db":

                databases_checked += 1


                if not self._sqlite_quick_check(
                    item
                ):

                    raise RuntimeError(
                        "SQLite quick_check invalide : "
                        +
                        str(
                            item.relative_to(
                                work_directory
                            )
                        )
                    )


                databases_valid += 1


        return {
            "success":
                True,

            "status":
                "VALID",

            "files_checked":
                files_checked,

            "databases_checked":
                databases_checked,

            "databases_valid":
                databases_valid,
        }


    # ========================================================
    # EXECUTE MIGRATION
    # ========================================================

    def execute_migration(
        self,
        backup_id,
    ):

        preflight = self.preflight(
            backup_id
        )


        if (
            preflight[
                "status"
            ]
            ==
            "MIGRATION_NOT_REQUIRED"
        ):

            return {
                **preflight,

                "executed_steps":
                    0,

                "work_copy_created":
                    False,

                "original_backup_modified":
                    False,
            }


        if not preflight[
            "success"
        ]:

            return {
                **preflight,

                "executed_steps":
                    0,

                "work_copy_created":
                    False,

                "original_backup_modified":
                    False,
            }


        source_directory = (
            self._backup_directory(
                backup_id
            )
        )


        original_before = (
            self._tree_fingerprint(
                source_directory
            )
        )


        chain = (
            self.registry
            .find_chain(
                source_version=
                    preflight[
                        "source_version"
                    ],

                target_version=
                    preflight[
                        "target_version"
                    ],
            )
        )


        if chain is None:

            raise RuntimeError(
                "Chaîne migration disparue "
                "après préflight."
            )


        prepared = (
            self.prepare_work_copy(
                backup_id
            )
        )


        work_directory = Path(
            prepared[
                "work_directory"
            ]
        ).resolve()


        work_root = (
            self.work_root
            .resolve()
        )


        try:

            work_directory.relative_to(
                work_root
            )

        except ValueError:

            raise RuntimeError(
                "Copie migration hors work_root."
            )


        state_path = (
            work_directory
            /
            "migration_state.json"
        )

        journal_path = (
            work_directory
            /
            "migration_journal.json"
        )


        journal = {
            "backup_id":
                backup_id,

            "source_version":
                preflight[
                    "source_version"
                ],

            "target_version":
                preflight[
                    "target_version"
                ],

            "started_at":
                self._utc_now_iso(),

            "completed_at":
                None,

            "status":
                "IN_PROGRESS",

            "steps":
                [],
        }


        current_version = (
            preflight[
                "source_version"
            ]
        )


        state = {
            "backup_id":
                backup_id,

            "source_version":
                preflight[
                    "source_version"
                ],

            "current_version":
                current_version,

            "target_version":
                preflight[
                    "target_version"
                ],

            "status":
                "IN_PROGRESS",

            "original_backup_modified":
                False,
        }


        self._atomic_json_write(
            state_path,
            state,
        )

        self._atomic_json_write(
            journal_path,
            journal,
        )


        try:

            for index, step in enumerate(
                chain,
                start=1,
            ):

                source_version = (
                    step[
                        "source_version"
                    ]
                )

                target_version = (
                    step[
                        "target_version"
                    ]
                )


                if (
                    current_version
                    !=
                    source_version
                ):

                    raise RuntimeError(
                        "Ordre de migration incohérent."
                    )


                migration = step[
                    "migration"
                ]


                result = migration(
                    work_directory
                )


                if not isinstance(
                    result,
                    dict,
                ):

                    raise RuntimeError(
                        "Résultat migration invalide."
                    )


                if (
                    result.get(
                        "success"
                    )
                    is not True
                ):

                    raise RuntimeError(
                        "Étape migration échouée : "
                        +
                        source_version
                        +
                        " -> "
                        +
                        target_version
                    )


                # Le journal doit rester sérialisable.
                try:

                    json.dumps(
                        result,
                        ensure_ascii=False,
                    )

                except TypeError as error:

                    raise RuntimeError(
                        "Résultat migration "
                        "non sérialisable."
                    ) from error


                validation = (
                    self._validate_work_copy(
                        work_directory
                    )
                )


                current_version = (
                    target_version
                )


                journal[
                    "steps"
                ].append(
                    {
                        "index":
                            index,

                        "source_version":
                            source_version,

                        "target_version":
                            target_version,

                        "completed_at":
                            self._utc_now_iso(),

                        "result":
                            result,

                        "validation":
                            validation,
                    }
                )


                state[
                    "current_version"
                ] = current_version


                self._atomic_json_write(
                    state_path,
                    state,
                )

                self._atomic_json_write(
                    journal_path,
                    journal,
                )


            if (
                current_version
                !=
                preflight[
                    "target_version"
                ]
            ):

                raise RuntimeError(
                    "Version finale de migration incohérente."
                )


            final_validation = (
                self._validate_work_copy(
                    work_directory
                )
            )


            original_after = (
                self._tree_fingerprint(
                    source_directory
                )
            )


            original_modified = (
                original_before
                !=
                original_after
            )


            if original_modified:

                raise RuntimeError(
                    "Le backup original a été modifié."
                )


            state[
                "current_version"
            ] = current_version

            state[
                "status"
            ] = "COMPLETED"

            state[
                "original_backup_modified"
            ] = False


            journal[
                "status"
            ] = "COMPLETED"

            journal[
                "completed_at"
            ] = self._utc_now_iso()


            self._atomic_json_write(
                state_path,
                state,
            )

            self._atomic_json_write(
                journal_path,
                journal,
            )


            return {
                "success":
                    True,

                "status":
                    "MIGRATION_EXECUTED",

                "backup_id":
                    backup_id,

                "source_version":
                    preflight[
                        "source_version"
                    ],

                "target_version":
                    preflight[
                        "target_version"
                    ],

                "final_version":
                    current_version,

                "executed_steps":
                    len(
                        journal[
                            "steps"
                        ]
                    ),

                "work_copy_created":
                    True,

                "work_directory":
                    str(
                        work_directory
                    ),

                "journal_path":
                    str(
                        journal_path
                    ),

                "state_path":
                    str(
                        state_path
                    ),

                "validation":
                    final_validation,

                "original_backup_modified":
                    False,
            }


        except Exception as error:

            original_after = (
                self._tree_fingerprint(
                    source_directory
                )
            )


            original_modified = (
                original_before
                !=
                original_after
            )


            state[
                "status"
            ] = "FAILED"

            state[
                "current_version"
            ] = current_version

            state[
                "original_backup_modified"
            ] = original_modified


            journal[
                "status"
            ] = "FAILED"

            journal[
                "completed_at"
            ] = self._utc_now_iso()

            journal[
                "error"
            ] = {
                "type":
                    type(
                        error
                    ).__name__,

                "message":
                    str(
                        error
                    ),
            }


            try:

                self._atomic_json_write(
                    state_path,
                    state,
                )

                self._atomic_json_write(
                    journal_path,
                    journal,
                )

            except Exception:

                pass


            return {
                "success":
                    False,

                "status":
                    "MIGRATION_FAILED",

                "backup_id":
                    backup_id,

                "source_version":
                    preflight[
                        "source_version"
                    ],

                "target_version":
                    preflight[
                        "target_version"
                    ],

                "current_version":
                    current_version,

                "executed_steps":
                    len(
                        journal[
                            "steps"
                        ]
                    ),

                "work_copy_created":
                    True,

                "work_directory":
                    str(
                        work_directory
                    ),

                "error":
                    type(
                        error
                    ).__name__,

                "message":
                    str(
                        error
                    ),

                "original_backup_modified":
                    original_modified,
            }


    # ========================================================
    # SAFE ARCHIVE PATH
    # ========================================================

    @staticmethod
    def _safe_archive_path(
        value,
    ):

        value = str(
            value
            or
            ""
        ).strip()

        relative = Path(
            value
        )


        if (
            not value
            or
            relative.is_absolute()
            or
            ".." in relative.parts
        ):

            raise RuntimeError(
                "Chemin archive migration invalide."
            )


        return relative


    # ========================================================
    # COPY PUBLISHED FILE
    # ========================================================

    def _copy_published_file(
        self,
        *,
        source,
        destination,
    ):

        source = Path(
            source
        )

        destination = Path(
            destination
        )


        if (
            not source.is_file()
            or
            source.is_symlink()
        ):

            raise RuntimeError(
                "Source publication migration invalide."
            )


        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            destination.parent,
            0o700,
        )


        if (
            destination.exists()
            or
            destination.is_symlink()
        ):

            raise RuntimeError(
                "Destination publication déjà présente."
            )


        temporary = (
            destination.parent
            /
            (
                "."
                +
                destination.name
                +
                ".publish-part"
            )
        )


        if (
            temporary.exists()
            or
            temporary.is_symlink()
        ):

            raise RuntimeError(
                "Temporaire publication déjà présent."
            )


        try:

            with source.open(
                "rb"
            ) as source_handle:

                with temporary.open(
                    "xb"
                ) as target_handle:

                    shutil.copyfileobj(
                        source_handle,
                        target_handle,
                        length=
                            1024
                            *
                            1024,
                    )

                    target_handle.flush()

                    os.fsync(
                        target_handle.fileno()
                    )


            os.chmod(
                temporary,
                0o600,
            )


            source_hash = (
                sha256_file(
                    source
                )
            )

            target_hash = (
                sha256_file(
                    temporary
                )
            )


            if source_hash != target_hash:

                raise RuntimeError(
                    "SHA-256 publication incohérent."
                )


            os.replace(
                temporary,
                destination,
            )

            os.chmod(
                destination,
                0o600,
            )

            self._fsync_directory(
                destination.parent
            )


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    # ========================================================
    # PUBLISH MIGRATED BACKUP
    # ========================================================

    def publish_migrated_backup(
        self,
        *,
        source_backup_id,
        work_directory,
        source_version,
        target_version,
        executed_steps,
        actor="MIGRATION_SERVICE",
    ):

        source_backup_id = (
            validate_backup_id(
                source_backup_id
            )
        )


        source_directory = (
            self._backup_directory(
                source_backup_id
            )
        )


        original_before = (
            self._tree_fingerprint(
                source_directory
            )
        )


        source_manifest = (
            self._read_manifest(
                source_directory
            )
        )


        source_files = (
            source_manifest.get(
                "files"
            )
        )


        if not isinstance(
            source_files,
            list,
        ):

            raise RuntimeError(
                "Manifest source sans fichiers."
            )


        work_directory = Path(
            work_directory
        ).resolve()


        if (
            not work_directory.is_dir()
            or
            work_directory.is_symlink()
        ):

            raise RuntimeError(
                "Copie de migration invalide."
            )


        work_root = (
            self.work_root
            .resolve()
        )


        try:

            work_directory.relative_to(
                work_root
            )

        except ValueError:

            raise RuntimeError(
                "Copie de migration hors work_root."
            )


        state_path = (
            work_directory
            /
            "migration_state.json"
        )


        if (
            not state_path.is_file()
            or
            state_path.is_symlink()
        ):

            raise RuntimeError(
                "État migration absent."
            )


        state = json.loads(
            state_path.read_text(
                encoding="utf-8"
            )
        )


        if (
            state.get(
                "status"
            )
            !=
            "COMPLETED"
        ):

            raise RuntimeError(
                "Migration non terminée."
            )


        if (
            state.get(
                "current_version"
            )
            !=
            target_version
        ):

            raise RuntimeError(
                "Version finale migration incohérente."
            )


        # ====================================================
        # NEW BACKUP ID
        # ====================================================

        new_backup_id = (
            backup_service
            ._new_backup_id()
        )


        destination_root = (
            self.backup_root
            .resolve()
        )


        destination_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            destination_root,
            0o700,
        )


        partial_directory = (
            destination_root
            /
            (
                new_backup_id
                +
                ".partial"
            )
        )


        final_directory = (
            destination_root
            /
            new_backup_id
        )


        if (
            partial_directory.exists()
            or
            partial_directory.is_symlink()
            or
            final_directory.exists()
            or
            final_directory.is_symlink()
        ):

            raise RuntimeError(
                "Destination backup migré déjà existante."
            )


        partial_directory.mkdir(
            parents=False,
            exist_ok=False,
        )

        os.chmod(
            partial_directory,
            0o700,
        )


        published_files = []


        try:

            # =================================================
            # COPY ONLY RESTORABLE MANIFEST FILES
            # =================================================

            for entry in source_files:

                if not isinstance(
                    entry,
                    dict,
                ):

                    raise RuntimeError(
                        "Entrée manifest source invalide."
                    )


                archive_relative = (
                    self._safe_archive_path(
                        entry.get(
                            "archive_path"
                        )
                    )
                )


                source = (
                    work_directory
                    /
                    archive_relative
                ).resolve()


                try:

                    source.relative_to(
                        work_directory
                    )

                except ValueError:

                    raise RuntimeError(
                        "Source migration hors work_directory."
                    )


                destination = (
                    partial_directory
                    /
                    archive_relative
                ).resolve()


                try:

                    destination.relative_to(
                        partial_directory.resolve()
                    )

                except ValueError:

                    raise RuntimeError(
                        "Destination backup migré "
                        "hors périmètre."
                    )


                self._copy_published_file(
                    source=
                        source,

                    destination=
                        destination,
                )


                category = str(
                    entry.get(
                        "category"
                    )
                    or
                    ""
                )


                sqlite_valid = None


                if category == "DATABASE":

                    sqlite_valid = (
                        self._sqlite_quick_check(
                            destination
                        )
                    )


                    if not sqlite_valid:

                        raise RuntimeError(
                            "SQLite migrée invalide : "
                            +
                            str(
                                archive_relative
                            )
                        )


                published_files.append(
                    {
                        "source_path":
                            entry.get(
                                "source_path"
                            ),

                        "archive_path":
                            str(
                                archive_relative
                            ),

                        "category":
                            category,

                        "sensitive":
                            bool(
                                entry.get(
                                    "sensitive"
                                )
                            ),

                        "size_bytes":
                            destination
                            .stat()
                            .st_size,

                        "sha256":
                            sha256_file(
                                destination
                            ),

                        "sqlite_quick_check":
                            sqlite_valid,
                    }
                )


            # =================================================
            # NEW STANDARD PHOENIX MANIFEST
            # =================================================

            manifest = build_manifest(
                backup_id=
                    new_backup_id,

                actor=
                    actor,

                backup_type=
                    "MIGRATED",

                files=
                    published_files,
            )


            # Provenance non restaurable :
            # metadata uniquement dans le manifest.
            manifest[
                "migration"
            ] = {
                "source_backup_id":
                    source_backup_id,

                "source_version":
                    source_version,

                "target_version":
                    target_version,

                "executed_steps":
                    int(
                        executed_steps
                    ),
            }


            write_manifest(
                partial_directory,
                manifest,
            )


            if (
                verify_manifest_hash(
                    partial_directory
                )
                is not True
            ):

                raise RuntimeError(
                    "Hash du manifest migré invalide."
                )


            # =================================================
            # VALIDATE PUBLISHED DATABASES
            # =================================================

            published_validation = (
                self._validate_work_copy(
                    partial_directory
                )
            )


            # =================================================
            # ORIGINAL MUST STILL BE IMMUTABLE
            # =================================================

            original_after = (
                self._tree_fingerprint(
                    source_directory
                )
            )


            if original_before != original_after:

                raise RuntimeError(
                    "Backup original modifié "
                    "pendant publication."
                )


            # =================================================
            # ATOMIC PUBLICATION
            # =================================================

            partial_directory.rename(
                final_directory
            )

            self._fsync_directory(
                destination_root
            )


            return {
                "success":
                    True,

                "status":
                    "MIGRATED_BACKUP_PUBLISHED",

                "source_backup_id":
                    source_backup_id,

                "backup_id":
                    new_backup_id,

                "source_version":
                    source_version,

                "target_version":
                    target_version,

                "executed_steps":
                    int(
                        executed_steps
                    ),

                "file_count":
                    len(
                        published_files
                    ),

                "validation":
                    published_validation,

                "backup_directory":
                    str(
                        final_directory
                    ),

                "original_backup_modified":
                    False,

                "migration_metadata_published":
                    True,
            }


        except Exception:

            if partial_directory.exists():

                shutil.rmtree(
                    partial_directory,
                    ignore_errors=True,
                )


            raise


    # ========================================================
    # EXECUTE + PUBLISH
    # ========================================================

    def migrate_and_publish(
        self,
        backup_id,
        *,
        actor="MIGRATION_SERVICE",
    ):

        migration = (
            self.execute_migration(
                backup_id
            )
        )


        if not migration.get(
            "success"
        ):

            return {
                **migration,

                "published":
                    False,
            }


        if (
            migration.get(
                "status"
            )
            ==
            "MIGRATION_NOT_REQUIRED"
        ):

            return {
                **migration,

                "published":
                    False,
            }


        publication = (
            self.publish_migrated_backup(
                source_backup_id=
                    backup_id,

                work_directory=
                    migration[
                        "work_directory"
                    ],

                source_version=
                    migration[
                        "source_version"
                    ],

                target_version=
                    migration[
                        "target_version"
                    ],

                executed_steps=
                    migration[
                        "executed_steps"
                    ],

                actor=
                    actor,
            )
        )


        return {
            "success":
                True,

            "status":
                "MIGRATION_PUBLISHED",

            "migration":
                migration,

            "publication":
                publication,

            "published":
                True,

            "original_backup_modified":
                False,
        }



backup_migration_service = (
    BackupMigrationService()
)
