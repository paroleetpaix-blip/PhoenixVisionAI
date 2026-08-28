"""
============================================================
PHOENIX VISION AI

Live Restore Transaction Planner

Phoenix Security Technologies
============================================================

Construit le plan transactionnel d'une restauration LIVE.

IMPORTANT
---------
Ce module ne modifie AUCUNE donnée Phoenix active.
Il produit uniquement un plan vérifié.
"""

from pathlib import Path

from core.backups.backup_manifest import (
    sha256_file,
)

from core.backups.restore_request import (
    REQUEST_ID_PATTERN,
)


class LiveRestoreTransactionPlanner:

    # ========================================================
    # SAFE CHILD
    # ========================================================

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
                "Chemin transaction invalide."
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
                "Chemin transaction "
                "hors périmètre."
            )


        return candidate


    # ========================================================
    # STAGED SOURCE
    # ========================================================

    def _verified_staged_file(
        self,
        *,
        root,
        archive_path,
        expected_sha256,
    ):

        path = self._safe_child(
            root,
            archive_path,
        )


        if (
            not path.is_file()
            or
            path.is_symlink()
        ):

            raise RuntimeError(
                "Fichier staging absent ou invalide : "
                +
                str(
                    archive_path
                )
            )


        actual_hash = (
            sha256_file(
                path
            )
        )


        if (
            expected_sha256
            and
            actual_hash.lower()
            !=
            str(
                expected_sha256
            ).lower()
        ):

            raise RuntimeError(
                "SHA-256 staging incohérent : "
                +
                str(
                    archive_path
                )
            )


        return path


    # ========================================================
    # BUILD
    # ========================================================

    def build(
        self,
        *,
        project_root,
        request_id,
        reconciliation,
        staging,
    ):

        project_root = Path(
            project_root
        ).resolve()


        request_id = str(
            request_id
            or
            ""
        ).strip()


        if not REQUEST_ID_PATTERN.fullmatch(
            request_id
        ):

            raise ValueError(
                "Request ID transaction invalide."
            )


        if (
            reconciliation.get(
                "write_performed"
            )
            is not False
        ):

            raise RuntimeError(
                "Réconciliation déjà modifiée."
            )


        if (
            reconciliation.get(
                "active_data_modified"
            )
            is not False
        ):

            raise RuntimeError(
                "État actif déjà modifié."
            )


        staging_directory = Path(
            staging[
                "staging_directory"
            ]
        ).resolve()

        restore_directory = (
            staging_directory
            /
            "restore"
        ).resolve()

        rollback_directory = (
            staging_directory
            /
            "rollback"
        ).resolve()


        if (
            not restore_directory.is_dir()
            or
            restore_directory.is_symlink()
        ):

            raise RuntimeError(
                "Staging Restore invalide."
            )


        if (
            not rollback_directory.is_dir()
            or
            rollback_directory.is_symlink()
        ):

            raise RuntimeError(
                "Staging Rollback invalide."
            )


        operations = []

        counts = {
            "KEEP":
                0,

            "REPLACE":
                0,

            "CREATE":
                0,

            "QUARANTINE":
                0,
        }


        for item in reconciliation[
            "actions"
        ]:

            action = item[
                "action"
            ]

            category = item[
                "category"
            ]

            target_relative = Path(
                item[
                    "target"
                ]
            )


            target = self._safe_child(
                project_root,
                target_relative,
            )


            if action not in counts:

                raise RuntimeError(
                    "Action transaction inconnue."
                )


            counts[
                action
            ] += 1


            # =================================================
            # KEEP
            # =================================================

            if action == "KEEP":

                operations.append(
                    {
                        "action":
                            "KEEP",

                        "category":
                            category,

                        "target":
                            str(
                                target_relative
                            ),

                        "active_write":
                            False,

                        "rollback_action":
                            "NONE",

                        "sqlite_sidecars":
                            [],
                    }
                )

                continue


            # =================================================
            # RESTORE SOURCE
            # =================================================

            if action in {
                "REPLACE",
                "CREATE",
            }:

                archive_path = item[
                    "archive_path"
                ]


                restore_source = (
                    self._verified_staged_file(
                        root=
                            restore_directory,

                        archive_path=
                            archive_path,

                        expected_sha256=
                            item.get(
                                "expected_sha256"
                            ),
                    )
                )


                restore_relative = (
                    restore_source.relative_to(
                        staging_directory
                    )
                )


            else:

                archive_path = None
                restore_relative = None


            # =================================================
            # REPLACE
            # =================================================

            if action == "REPLACE":

                rollback_source = (
                    self._safe_child(
                        rollback_directory,
                        archive_path,
                    )
                )


                if (
                    not rollback_source.is_file()
                    or
                    rollback_source.is_symlink()
                ):

                    raise RuntimeError(
                        "Rollback staging absent : "
                        +
                        str(
                            archive_path
                        )
                    )


                rollback_relative = (
                    rollback_source.relative_to(
                        staging_directory
                    )
                )


                operation = {
                    "action":
                        "REPLACE",

                    "category":
                        category,

                    "target":
                        str(
                            target_relative
                        ),

                    "restore_source":
                        str(
                            restore_relative
                        ),

                    "active_write":
                        True,

                    "rollback_action":
                        "RESTORE_SNAPSHOT",

                    "fallback_rollback_action":
                        "RESTORE_PRE_RESTORE",

                    "fallback_rollback_source":
                        str(
                            rollback_relative
                        ),
                }


            # =================================================
            # CREATE
            # =================================================

            elif action == "CREATE":

                operation = {
                    "action":
                        "CREATE",

                    "category":
                        category,

                    "target":
                        str(
                            target_relative
                        ),

                    "restore_source":
                        str(
                            restore_relative
                        ),

                    "active_write":
                        True,

                    "rollback_action":
                        "DELETE_CREATED",
                }


            # =================================================
            # QUARANTINE
            # =================================================

            elif action == "QUARANTINE":

                quarantine_relative = (
                    Path(
                        "quarantine"
                    )
                    /
                    target_relative
                )


                quarantine_target = (
                    self._safe_child(
                        staging_directory,
                        quarantine_relative,
                    )
                )


                operation = {
                    "action":
                        "QUARANTINE",

                    "category":
                        category,

                    "target":
                        str(
                            target_relative
                        ),

                    "quarantine_target":
                        str(
                            quarantine_target.relative_to(
                                staging_directory
                            )
                        ),

                    "active_write":
                        True,

                    "rollback_action":
                        "RESTORE_QUARANTINE",
                }


            else:

                raise RuntimeError(
                    "Action transaction non supportée."
                )


            # =================================================
            # SQLITE SIDECARS
            # =================================================

            if (
                category
                ==
                "DATABASE"
                and
                action
                in {
                    "REPLACE",
                    "CREATE",
                }
            ):

                operation[
                    "sqlite_sidecars"
                ] = [
                    str(
                        Path(
                            str(
                                target_relative
                            )
                            +
                            "-wal"
                        )
                    ),
                    str(
                        Path(
                            str(
                                target_relative
                            )
                            +
                            "-shm"
                        )
                    ),
                ]


            else:

                operation[
                    "sqlite_sidecars"
                ] = []


            operations.append(
                operation
            )


        # ====================================================
        # EXECUTION ORDER
        # ====================================================

        priority = {
            "KEEP":
                0,

            "QUARANTINE":
                10,

            "REPLACE":
                20,

            "CREATE":
                30,
        }


        operations.sort(
            key=lambda item: (
                priority[
                    item[
                        "action"
                    ]
                ],
                item[
                    "target"
                ],
            )
        )


        active_operations = [
            item
            for item
            in operations
            if item[
                "active_write"
            ]
        ]


        sidecars = sorted(
            {
                sidecar
                for item
                in operations
                for sidecar
                in item.get(
                    "sqlite_sidecars",
                    [],
                )
            }
        )


        return {
            "status":
                "LIVE_TRANSACTION_PLAN_READY",

            "request_id":
                request_id,

            "counts":
                counts,

            "operations":
                operations,

            "total_operations":
                len(
                    operations
                ),

            "active_operations":
                len(
                    active_operations
                ),

            "sqlite_sidecars":
                sidecars,

            "sqlite_sidecar_count":
                len(
                    sidecars
                ),

            "write_performed":
                False,

            "active_data_modified":
                False,

            "transaction_execution_enabled":
                False,
        }


live_restore_transaction_planner = (
    LiveRestoreTransactionPlanner()
)
