"""
============================================================
PHOENIX VISION AI

Live Restore Transaction Snapshot

Phoenix Security Technologies
============================================================

Capture l'état exact des fichiers actifs qui seront modifiés
par une restauration LIVE.

Le snapshot est créé AVANT la première écriture active.
"""

import os
import shutil

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)

from core.backups.restore_request import (
    REQUEST_ID_PATTERN,
)


class LiveRestoreSnapshot:

    @staticmethod
    def _safe_child(
        root,
        relative,
    ):

        root = Path(
            root
        ).resolve()

        relative = Path(
            str(
                relative
                or
                ""
            )
        )


        if (
            not str(relative)
            or
            relative.is_absolute()
            or
            ".." in relative.parts
        ):

            raise RuntimeError(
                "Chemin snapshot invalide."
            )


        candidate = (
            root
            /
            relative
        ).resolve()


        try:

            candidate.relative_to(
                root
            )

        except ValueError:

            raise RuntimeError(
                "Chemin snapshot hors périmètre."
            )


        return candidate


    @staticmethod
    def _secure_directory(
        path,
    ):

        path = Path(
            path
        )


        if (
            path.exists()
            and
            path.is_symlink()
        ):

            raise RuntimeError(
                "Répertoire snapshot symbolique interdit."
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


    def _copy_file(
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
                "Source snapshot invalide."
            )


        self._secure_directory(
            destination.parent
        )


        temporary = (
            destination.parent
            /
            (
                "."
                +
                destination.name
                +
                ".snapshot-part"
            )
        )


        if (
            destination.exists()
            or
            destination.is_symlink()
            or
            temporary.exists()
            or
            temporary.is_symlink()
        ):

            raise RuntimeError(
                "Destination snapshot déjà existante."
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

            copy_hash = (
                sha256_file(
                    temporary
                )
            )


            if source_hash != copy_hash:

                raise RuntimeError(
                    "SHA-256 snapshot incohérent."
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
                    copy_hash,
            }


        finally:

            if temporary.exists():

                try:

                    temporary.unlink()

                except OSError:

                    pass


    def create(
        self,
        *,
        project_root,
        request_id,
        transaction,
        staging_directory,
    ):

        project_root = Path(
            project_root
        ).resolve()

        staging_directory = Path(
            staging_directory
        ).resolve()


        if not REQUEST_ID_PATTERN.fullmatch(
            str(
                request_id
            )
        ):

            raise ValueError(
                "Request ID snapshot invalide."
            )


        snapshot_root = (
            staging_directory
            /
            "current"
        )


        if (
            snapshot_root.exists()
            or
            snapshot_root.is_symlink()
        ):

            raise RuntimeError(
                "Snapshot transactionnel déjà présent."
            )


        snapshot_root.mkdir(
            parents=False,
            exist_ok=False,
        )

        os.chmod(
            snapshot_root,
            0o700,
        )


        items = []

        sidecars = []

        seen = set()


        try:

            for operation in transaction[
                "operations"
            ]:

                if not operation.get(
                    "active_write"
                ):

                    continue


                action = operation[
                    "action"
                ]


                if action not in {
                    "REPLACE",
                    "QUARANTINE",
                }:

                    continue


                target_relative = (
                    operation[
                        "target"
                    ]
                )

                target = self._safe_child(
                    project_root,
                    target_relative,
                )


                if (
                    target.exists()
                    or
                    target.is_symlink()
                ):

                    if (
                        not target.is_file()
                        or
                        target.is_symlink()
                    ):

                        raise RuntimeError(
                            "Cible snapshot invalide."
                        )


                    destination = (
                        self._safe_child(
                            snapshot_root,
                            target_relative,
                        )
                    )


                    result = self._copy_file(
                        source=
                            target,

                        destination=
                            destination,
                    )


                    seen.add(
                        str(
                            target_relative
                        )
                    )


                    items.append(
                        {
                            "target":
                                str(
                                    target_relative
                                ),

                            "size":
                                result[
                                    "size"
                                ],

                            "sha256":
                                result[
                                    "sha256"
                                ],
                        }
                    )


                for sidecar_relative in operation.get(
                    "sqlite_sidecars",
                    [],
                ):

                    sidecar = self._safe_child(
                        project_root,
                        sidecar_relative,
                    )


                    if not sidecar.exists():

                        continue


                    if (
                        not sidecar.is_file()
                        or
                        sidecar.is_symlink()
                    ):

                        raise RuntimeError(
                            "Sidecar SQLite snapshot invalide."
                        )


                    destination = (
                        self._safe_child(
                            snapshot_root,
                            sidecar_relative,
                        )
                    )


                    result = self._copy_file(
                        source=
                            sidecar,

                        destination=
                            destination,
                    )


                    sidecars.append(
                        {
                            "target":
                                str(
                                    sidecar_relative
                                ),

                            "size":
                                result[
                                    "size"
                                ],

                            "sha256":
                                result[
                                    "sha256"
                                ],
                        }
                    )


            return {
                "success":
                    True,

                "status":
                    "TRANSACTION_SNAPSHOT_READY",

                "request_id":
                    str(
                        request_id
                    ),

                "snapshot_directory":
                    str(
                        snapshot_root
                    ),

                "files":
                    len(
                        items
                    ),

                "sidecars":
                    len(
                        sidecars
                    ),

                "items":
                    items,

                "sidecar_items":
                    sidecars,

                "active_data_modified":
                    False,
            }


        except Exception:

            shutil.rmtree(
                snapshot_root,
                ignore_errors=True,
            )

            raise


live_restore_snapshot = (
    LiveRestoreSnapshot()
)
