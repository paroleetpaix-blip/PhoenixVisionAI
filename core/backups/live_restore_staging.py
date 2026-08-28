"""
============================================================
PHOENIX VISION AI

Live Restore Staging

Phoenix Security Technologies
============================================================

Prépare une restauration LIVE dans un espace isolé.

Aucune donnée Phoenix active n'est modifiée ici.
"""

import json
import os
import shutil
import sqlite3

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)

from core.backups.restore_request import (
    REQUEST_ID_PATTERN,
)


def utc_now_iso():

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            microsecond=0
        )
        .isoformat()
    )


class LiveRestoreStaging:

    # ========================================================
    # DIRECTORY
    # ========================================================

    @staticmethod
    def _secure_directory(
        path,
    ):

        path = Path(
            path
        )

        if path.exists() and path.is_symlink():

            raise RuntimeError(
                "Répertoire de staging symbolique interdit."
            )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        os.chmod(
            path,
            0o700,
        )

        return path


    # ========================================================
    # SAFE PATH
    # ========================================================

    @staticmethod
    def _archive_relative_path(
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
                "Chemin archive staging invalide."
            )


        return relative


    # ========================================================
    # SQLITE
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
            str(path)
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
    # ATOMIC COPY
    # ========================================================

    def _copy_one(
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
                "Source staging invalide."
            )


        self._secure_directory(
            destination.parent
        )


        if (
            destination.exists()
            or
            destination.is_symlink()
        ):

            raise RuntimeError(
                "Destination staging déjà existante."
            )


        temporary = (
            destination.parent
            /
            (
                "."
                +
                destination.name
                +
                ".part"
            )
        )


        if (
            temporary.exists()
            or
            temporary.is_symlink()
        ):

            raise RuntimeError(
                "Fichier temporaire staging déjà présent."
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


            if (
                source.stat().st_size
                !=
                temporary.stat().st_size
            ):

                raise RuntimeError(
                    "Taille staging incohérente."
                )


            source_hash = sha256_file(
                source
            )

            staged_hash = sha256_file(
                temporary
            )


            if source_hash != staged_hash:

                raise RuntimeError(
                    "Empreinte SHA-256 staging incohérente."
                )


            os.replace(
                temporary,
                destination,
            )

            os.chmod(
                destination,
                0o600,
            )


            return {
                "size":
                    destination.stat().st_size,

                "sha256":
                    staged_hash,
            }


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    # ========================================================
    # MANIFEST COPY
    # ========================================================

    def _stage_manifest(
        self,
        *,
        backup_directory,
        manifest,
        destination_root,
    ):

        backup_directory = Path(
            backup_directory
        ).resolve()

        destination_root = Path(
            destination_root
        ).resolve()


        files = manifest.get(
            "files"
        )


        if not isinstance(
            files,
            list,
        ):

            raise RuntimeError(
                "Manifest staging invalide."
            )


        results = []

        database_count = 0


        for entry in files:

            if not isinstance(
                entry,
                dict,
            ):

                raise RuntimeError(
                    "Entrée manifest staging invalide."
                )


            relative = (
                self._archive_relative_path(
                    entry.get(
                        "archive_path"
                    )
                )
            )


            source = (
                backup_directory
                /
                relative
            ).resolve()


            try:

                source.relative_to(
                    backup_directory
                )

            except ValueError:

                raise RuntimeError(
                    "Source staging hors sauvegarde."
                )


            destination = (
                destination_root
                /
                relative
            ).resolve()


            try:

                destination.relative_to(
                    destination_root
                )

            except ValueError:

                raise RuntimeError(
                    "Destination staging hors périmètre."
                )


            copy_result = (
                self._copy_one(
                    source=
                        source,

                    destination=
                        destination,
                )
            )


            category = str(
                entry.get(
                    "category"
                )
                or
                ""
            )


            database_valid = None


            if category == "DATABASE":

                database_count += 1

                database_valid = (
                    self._sqlite_quick_check(
                        destination
                    )
                )


                if not database_valid:

                    raise RuntimeError(
                        "Base SQLite staging invalide : "
                        +
                        str(
                            relative
                        )
                    )


            results.append(
                {
                    "archive_path":
                        str(
                            relative
                        ),

                    "category":
                        category,

                    "size":
                        copy_result[
                            "size"
                        ],

                    "sha256":
                        copy_result[
                            "sha256"
                        ],

                    "database_valid":
                        database_valid,
                }
            )


        return {
            "files":
                len(
                    results
                ),

            "databases":
                database_count,

            "items":
                results,
        }


    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def _write_summary(
        path,
        payload,
    ):

        path = Path(
            path
        )


        if (
            path.exists()
            or
            path.is_symlink()
        ):

            raise RuntimeError(
                "Résumé staging déjà existant."
            )


        with path.open(
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
            path,
            0o600,
        )


    # ========================================================
    # PREPARE
    # ========================================================

    def prepare(
        self,
        *,
        request_id,
        backup_directory,
        backup_manifest,
        pre_restore_directory,
        pre_restore_manifest,
        staging_root,
    ):

        request_id = str(
            request_id
            or
            ""
        ).strip()


        if not REQUEST_ID_PATTERN.fullmatch(
            request_id
        ):

            raise ValueError(
                "Request ID staging invalide."
            )


        staging_root = (
            self._secure_directory(
                staging_root
            )
            .resolve()
        )


        request_directory = (
            staging_root
            /
            request_id
        )


        if (
            request_directory.exists()
            or
            request_directory.is_symlink()
        ):

            raise RuntimeError(
                "Un staging existe déjà "
                "pour cette restauration."
            )


        request_directory.mkdir(
            parents=False,
            exist_ok=False,
        )

        os.chmod(
            request_directory,
            0o700,
        )


        restore_directory = (
            request_directory
            /
            "restore"
        )

        rollback_directory = (
            request_directory
            /
            "rollback"
        )


        self._secure_directory(
            restore_directory
        )

        self._secure_directory(
            rollback_directory
        )


        try:

            restore_result = (
                self._stage_manifest(
                    backup_directory=
                        backup_directory,

                    manifest=
                        backup_manifest,

                    destination_root=
                        restore_directory,
                )
            )


            rollback_result = (
                self._stage_manifest(
                    backup_directory=
                        pre_restore_directory,

                    manifest=
                        pre_restore_manifest,

                    destination_root=
                        rollback_directory,
                )
            )


            summary = {
                "status":
                    "STAGING_READY",

                "request_id":
                    request_id,

                "prepared_at":
                    utc_now_iso(),

                "backup_id":
                    backup_manifest.get(
                        "backup_id"
                    ),

                "pre_restore_backup_id":
                    pre_restore_manifest.get(
                        "backup_id"
                    ),

                "restore_files":
                    restore_result[
                        "files"
                    ],

                "restore_databases":
                    restore_result[
                        "databases"
                    ],

                "rollback_files":
                    rollback_result[
                        "files"
                    ],

                "rollback_databases":
                    rollback_result[
                        "databases"
                    ],

                "active_data_modified":
                    False,
            }


            self._write_summary(
                request_directory
                /
                "staging_summary.json",

                summary,
            )


            return {
                **summary,

                "staging_directory":
                    str(
                        request_directory
                    ),

                "restore_directory":
                    str(
                        restore_directory
                    ),

                "rollback_directory":
                    str(
                        rollback_directory
                    ),
            }


        except Exception:

            # Le staging n'est pas une donnée active.
            # En cas d'échec de préparation, on supprime
            # uniquement le staging incomplet.
            shutil.rmtree(
                request_directory,
                ignore_errors=True,
            )

            raise


live_restore_staging = (
    LiveRestoreStaging()
)
