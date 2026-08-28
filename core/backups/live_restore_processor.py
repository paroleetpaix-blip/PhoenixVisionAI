"""
============================================================
PHOENIX VISION AI

Live Restore Processor

Phoenix Security Technologies
============================================================

IMPORTANT
---------
La première version de ce processeur est STRICTEMENT DRY-RUN.

Elle peut analyser une restauration destinée à l'installation
Phoenix réelle, mais elle n'effectue aucune écriture.
"""

import json

from pathlib import Path

from core import constants

from core.backups.restore_flags import (
    LIVE_RESTORE_ENABLED,
)

from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_policy import (
    PROJECT_ROOT,
    discover_database_sources,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
)

from core.backups.live_restore_reconciliation import (
    live_restore_reconciliation,
)

from core.backups.live_restore_snapshot import (
    live_restore_snapshot,
)

from core.backups.live_restore_transaction_executor import (
    isolated_transaction_executor,
)

from core.backups.live_restore_transaction import (
    live_restore_transaction_planner,
)

from core.backups.live_restore_staging import (
    live_restore_staging,
)

from core.backups.restore_request import (
    restore_request_store,
    validate_backup_id,
)

from core.backups.restore_service import (
    RestoreService,
)

from core.startup_lock import (
    phoenix_instance_lock,
)




class LiveRestoreProcessor:

    def __init__(
        self,
        *,
        catalog=backup_catalog,
        request_store=restore_request_store,
    ):

        self.catalog = catalog

        self.request_store = (
            request_store
        )

        self.target_resolver = (
            RestoreService()
        )


    # ========================================================
    # BACKUP DIRECTORY
    # ========================================================

    def _backup_directory(
        self,
        backup_id,
    ):

        backup_id = validate_backup_id(
            backup_id
        )

        root = Path(
            BACKUP_DIRECTORY
        ).resolve()

        path = (
            root
            /
            backup_id
        ).resolve()


        if path.parent != root:

            raise RuntimeError(
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
    # FULL BACKUP VERIFICATION
    # ========================================================

    def _verified_backup(
        self,
        backup_id,
    ):

        summary = (
            self.catalog
            .get_backup(
                backup_id,
                verify_files=True,
            )
        )


        if (
            summary.get(
                "status"
            )
            !=
            "AVAILABLE"
        ):

            raise RuntimeError(
                "Sauvegarde indisponible."
            )


        verification = (
            summary.get(
                "verification"
            )
            or
            {}
        )


        if not verification.get(
            "success"
        ):

            raise RuntimeError(
                "Intégrité complète "
                "de sauvegarde invalide."
            )


        return summary


    # ========================================================
    # CURRENT DATABASE ALLOWLIST
    # ========================================================

    def _allowed_database_targets(
        self,
    ):

        allowed = {}


        for source in (
            discover_database_sources()
        ):

            allowed[
                str(
                    source.archive_path
                )
            ] = (
                source.source_path
                .resolve()
            )


        return allowed


    # ========================================================
    # LIVE TARGET
    # ========================================================

    def resolve_live_target(
        self,
        entry,
    ):

        category = str(
            entry.get(
                "category"
            )
            or
            ""
        )

        archive_path = str(
            entry.get(
                "archive_path"
            )
            or
            ""
        )


        target = (
            self.target_resolver
            .resolve_restore_target(
                entry
            )
        ).resolve()


        project_root = (
            PROJECT_ROOT
            .resolve()
        )


        try:

            target.relative_to(
                project_root
            )

        except ValueError:

            raise RuntimeError(
                "Destination LIVE hors "
                "du projet Phoenix."
            )


        if category == "DATABASE":

            allowed = (
                self._allowed_database_targets()
            )


            expected = allowed.get(
                archive_path
            )


            if expected is None:

                raise RuntimeError(
                    "Base LIVE non autorisée : "
                    +
                    archive_path
                )


            if target != expected:

                raise RuntimeError(
                    "Destination de base LIVE "
                    "incohérente."
                )


        if (
            target.exists()
            and
            target.is_symlink()
        ):

            raise RuntimeError(
                "Destination LIVE symbolique interdite."
            )


        return target


    # ========================================================
    # MANIFEST
    # ========================================================

    def _read_manifest(
        self,
        backup_id,
    ):

        directory = (
            self._backup_directory(
                backup_id
            )
        )

        path = (
            directory
            /
            "manifest.json"
        )


        manifest = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )


        if not isinstance(
            manifest,
            dict,
        ):

            raise RuntimeError(
                "Manifest LIVE invalide."
            )


        if (
            manifest.get(
                "backup_id"
            )
            !=
            backup_id
        ):

            raise RuntimeError(
                "Identité manifest incohérente."
            )


        return (
            directory,
            manifest,
        )


    # ========================================================
    # RESTORE PLAN
    # ========================================================

    def _build_plan(
        self,
        backup_directory,
        manifest,
    ):

        files = manifest.get(
            "files"
        )


        if not isinstance(
            files,
            list,
        ):

            raise RuntimeError(
                "Liste des fichiers "
                "de restauration invalide."
            )


        plan = []

        targets = set()


        for entry in files:

            archive_path = str(
                entry.get(
                    "archive_path"
                )
                or
                ""
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
                    "Source backup hors périmètre."
                )


            if (
                not source.is_file()
                or
                source.is_symlink()
            ):

                raise RuntimeError(
                    "Source backup invalide."
                )


            target = (
                self.resolve_live_target(
                    entry
                )
            )


            key = str(
                target
            )


            if key in targets:

                raise RuntimeError(
                    "Destination LIVE dupliquée."
                )


            targets.add(
                key
            )


            relative_target = (
                target.relative_to(
                    PROJECT_ROOT.resolve()
                )
            )


            plan.append(
                {
                    "archive_path":
                        archive_path,

                    "category":
                        entry.get(
                            "category"
                        ),

                    "sensitive":
                        bool(
                            entry.get(
                                "sensitive"
                            )
                        ),

                    "target":
                        str(
                            relative_target
                        ),

                    "target_exists":
                        target.exists(),
                }
            )


        return plan


    # ========================================================
    # DRY RUN
    # ========================================================

    def dry_run_pending(
        self,
        *,
        request_store=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        # Une restauration LIVE, même en préparation,
        # doit appartenir à l'unique instance Phoenix.
        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "Verrou d'instance Phoenix absent."
            )


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "write_performed":
                    False,
            }


        backup_id = request[
            "backup_id"
        ]

        pre_restore_id = request[
            "pre_restore_backup_id"
        ]


        backup = (
            self._verified_backup(
                backup_id
            )
        )

        pre_restore = (
            self._verified_backup(
                pre_restore_id
            )
        )


        if (
            str(
                pre_restore.get(
                    "backup_type"
                )
                or
                ""
            ).upper()
            !=
            "PRE_RESTORE"
        ):

            raise RuntimeError(
                "Backup de sécurité "
                "non PRE_RESTORE."
            )


        application = getattr(
            constants,
            "APP_NAME",
            "Phoenix Vision AI",
        )

        current_version = getattr(
            constants,
            "VERSION",
            "unknown",
        )


        for item in (
            backup,
            pre_restore,
        ):

            if (
                item.get(
                    "application"
                )
                !=
                application
            ):

                raise RuntimeError(
                    "Application incompatible."
                )


            if (
                item.get(
                    "application_version"
                )
                !=
                current_version
            ):

                raise RuntimeError(
                    "Version incompatible. "
                    "La migration des sauvegardes "
                    "n'est pas encore active."
                )


        backup_directory, manifest = (
            self._read_manifest(
                backup_id
            )
        )


        plan = (
            self._build_plan(
                backup_directory,
                manifest,
            )
        )


        if (
            len(
                plan
            )
            !=
            int(
                backup.get(
                    "file_count",
                    -1,
                )
            )
        ):

            raise RuntimeError(
                "Nombre de fichiers LIVE incohérent."
            )


        database_count = sum(
            item[
                "category"
            ]
            ==
            "DATABASE"

            for item
            in plan
        )

        sensitive_count = sum(
            item[
                "sensitive"
            ]

            for item
            in plan
        )


        return {
            "success":
                True,

            "status":
                "LIVE_RESTORE_DRY_RUN_READY",

            "request_id":
                request[
                    "request_id"
                ],

            "backup_id":
                backup_id,

            "pre_restore_backup_id":
                pre_restore_id,

            "application":
                application,

            "version":
                current_version,

            "lock_acquired":
                True,

            "files":
                len(
                    plan
                ),

            "databases":
                database_count,

            "sensitive":
                sensitive_count,

            "backup_verification":
                backup[
                    "verification"
                ][
                    "status"
                ],

            "pre_restore_verification":
                pre_restore[
                    "verification"
                ][
                    "status"
                ],

            "plan":
                plan,

            "write_performed":
                False,

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,
        }

    # ========================================================
    # LIVE RECONCILIATION
    # ========================================================

    def build_reconciliation_pending(
        self,
        *,
        request_store=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "write_performed":
                    False,

                "active_data_modified":
                    False,
            }


        dry_run = (
            self.dry_run_pending(
                request_store=
                    store
            )
        )


        if not dry_run.get(
            "success"
        ):

            raise RuntimeError(
                "LIVE_DRY_RUN_FAILED"
            )


        backup_directory, manifest = (
            self._read_manifest(
                request[
                    "backup_id"
                ]
            )
        )


        reconciliation = (
            live_restore_reconciliation
            .build(
                project_root=
                    PROJECT_ROOT,

                backup_directory=
                    backup_directory,

                manifest=
                    manifest,

                target_resolver=
                    self.resolve_live_target,
            )
        )


        return {
            "success":
                True,

            "status":
                "LIVE_RESTORE_RECONCILIATION_READY",

            "request_id":
                request[
                    "request_id"
                ],

            "backup_id":
                request[
                    "backup_id"
                ],

            "pre_restore_backup_id":
                request[
                    "pre_restore_backup_id"
                ],

            "backup_files":
                reconciliation[
                    "backup_files"
                ],

            "total_actions":
                reconciliation[
                    "total_actions"
                ],

            "counts":
                reconciliation[
                    "counts"
                ],

            "actions":
                reconciliation[
                    "actions"
                ],

            "ignored_user_files":
                reconciliation[
                    "ignored_user_files"
                ],

            "write_performed":
                False,

            "active_data_modified":
                False,

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,
        }


    # ========================================================
    # LIVE STAGING
    # ========================================================

    def prepare_staging_pending(
        self,
        *,
        request_store=None,
        staging_root=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "staging_written":
                    False,

                "active_data_modified":
                    False,
            }


        # Le DRY-RUN constitue le préflight LIVE complet.
        dry_run = (
            self.dry_run_pending(
                request_store=
                    store
            )
        )


        if not dry_run.get(
            "success"
        ):

            raise RuntimeError(
                "LIVE_DRY_RUN_FAILED"
            )


        backup_directory, backup_manifest = (
            self._read_manifest(
                request[
                    "backup_id"
                ]
            )
        )


        (
            pre_restore_directory,
            pre_restore_manifest,
        ) = (
            self._read_manifest(
                request[
                    "pre_restore_backup_id"
                ]
            )
        )


        if staging_root is None:

            staging_root = (
                PROJECT_ROOT
                /
                "data"
                /
                ".restore-staging"
            )


        result = (
            live_restore_staging
            .prepare(
                request_id=
                    request[
                        "request_id"
                    ],

                backup_directory=
                    backup_directory,

                backup_manifest=
                    backup_manifest,

                pre_restore_directory=
                    pre_restore_directory,

                pre_restore_manifest=
                    pre_restore_manifest,

                staging_root=
                    staging_root,
            )
        )


        return {
            "success":
                True,

            "status":
                "LIVE_RESTORE_STAGING_READY",

            "request_id":
                request[
                    "request_id"
                ],

            "backup_id":
                request[
                    "backup_id"
                ],

            "pre_restore_backup_id":
                request[
                    "pre_restore_backup_id"
                ],

            "restore_files":
                result[
                    "restore_files"
                ],

            "restore_databases":
                result[
                    "restore_databases"
                ],

            "rollback_files":
                result[
                    "rollback_files"
                ],

            "rollback_databases":
                result[
                    "rollback_databases"
                ],

            "staging_directory":
                result[
                    "staging_directory"
                ],

            "staging_written":
                True,

            "active_data_modified":
                False,

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,
        }


    # ========================================================
    # LIVE TRANSACTION PLAN
    # ========================================================

    def build_transaction_pending(
        self,
        *,
        request_store=None,
        staging_root=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "write_performed":
                    False,

                "active_data_modified":
                    False,
            }


        reconciliation = (
            self.build_reconciliation_pending(
                request_store=
                    store
            )
        )


        staging = (
            self.prepare_staging_pending(
                request_store=
                    store,

                staging_root=
                    staging_root,
            )
        )


        transaction = (
            live_restore_transaction_planner
            .build(
                project_root=
                    PROJECT_ROOT,

                request_id=
                    request[
                        "request_id"
                    ],

                reconciliation=
                    reconciliation,

                staging=
                    staging,
            )
        )


        return {
            "success":
                True,

            **transaction,

            "staging_directory":
                staging[
                    "staging_directory"
                ],

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,
        }


    # ========================================================
    # LIVE TRANSACTION SNAPSHOT
    # ========================================================

    def prepare_transaction_snapshot_pending(
        self,
        *,
        request_store=None,
        staging_root=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "active_data_modified":
                    False,
            }


        transaction = (
            self.build_transaction_pending(
                request_store=
                    store,

                staging_root=
                    staging_root,
            )
        )


        result = (
            live_restore_snapshot
            .create(
                project_root=
                    PROJECT_ROOT,

                request_id=
                    request[
                        "request_id"
                    ],

                transaction=
                    transaction,

                staging_directory=
                    transaction[
                        "staging_directory"
                    ],
            )
        )


        return {
            "success":
                True,

            "status":
                "LIVE_TRANSACTION_SNAPSHOT_READY",

            "request_id":
                request[
                    "request_id"
                ],

            "transaction":
                transaction,

            "snapshot":
                result,

            "active_data_modified":
                False,

            "write_performed":
                False,

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,
        }


    # ========================================================
    # LIVE EXECUTION GATE
    # ========================================================

    # ========================================================
    # FINALIZE LIVE RESULT
    # ========================================================

    def _finalize_live_result(
        self,
        *,
        store,
        request,
        transaction,
        execution,
    ):

        engine_status = str(
            execution.get(
                "status"
            )
            or
            ""
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        if (
            execution.get(
                "success"
            )
            and
            engine_status
            ==
            "ISOLATED_TRANSACTION_RESTORED"
        ):

            journal = (
                store.write_result(
                    request=
                        request,

                    status=
                        "LIVE_RESTORE_RESTORED",

                    success=
                        True,

                    details={
                        "engine_status":
                            engine_status,

                        "active_operations_applied":
                            execution.get(
                                "active_operations_applied"
                            ),

                        "verification":
                            execution.get(
                                "verification"
                            ),
                    },
                )
            )


            store.remove_in_progress()


            return {
                "success":
                    True,

                "status":
                    "LIVE_RESTORE_RESTORED",

                "safe_state":
                    True,

                "write_performed":
                    True,

                "in_progress_removed":
                    True,

                "request_id":
                    request[
                        "request_id"
                    ],

                "journal":
                    journal,

                "execution":
                    execution,
            }


        # ====================================================
        # FAILED BUT ROLLED BACK SAFELY
        # ====================================================

        if (
            engine_status
            ==
            "ISOLATED_TRANSACTION_ROLLED_BACK"
            and
            execution.get(
                "safe_state"
            )
            is True
            and
            execution.get(
                "rollback_performed"
            )
            is True
        ):

            journal = (
                store.write_result(
                    request=
                        request,

                    status=
                        "LIVE_RESTORE_FAILED_ROLLED_BACK",

                    success=
                        False,

                    details={
                        "engine_status":
                            engine_status,

                        "restore_error":
                            execution.get(
                                "restore_error"
                            ),

                        "rollback_verification":
                            execution.get(
                                "rollback_verification"
                            ),
                    },
                )
            )


            store.remove_in_progress()


            return {
                "success":
                    False,

                "status":
                    "LIVE_RESTORE_FAILED_ROLLED_BACK",

                "safe_state":
                    True,

                "write_performed":
                    True,

                "in_progress_removed":
                    True,

                "request_id":
                    request[
                        "request_id"
                    ],

                "journal":
                    journal,

                "execution":
                    execution,
            }


        # ====================================================
        # CRITICAL FAILURE
        # ====================================================

        try:

            journal = (
                store.write_result(
                    request=
                        request,

                    status=
                        "LIVE_RESTORE_CRITICAL_FAILURE",

                    success=
                        False,

                    details={
                        "engine_status":
                            engine_status,

                        "restore_error":
                            execution.get(
                                "restore_error"
                            ),

                        "rollback_error":
                            execution.get(
                                "rollback_error"
                            ),
                    },
                )
            )

        except Exception:

            journal = None


        # IMPORTANT :
        # IN_PROGRESS reste présent.
        # Phoenix restera bloqué au prochain démarrage.
        return {
            "success":
                False,

            "status":
                "LIVE_RESTORE_CRITICAL_FAILURE",

            "safe_state":
                False,

            "write_performed":
                True,

            "in_progress_removed":
                False,

            "request_id":
                request[
                    "request_id"
                ],

            "journal":
                journal,

            "execution":
                execution,
        }


    # ========================================================
    # LIVE EXECUTION
    # ========================================================

    def execute_pending(
        self,
        *,
        request_store=None,
        staging_root=None,
    ):

        store = (
            request_store
            or
            self.request_store
        )


        # ====================================================
        # INSTANCE LOCK
        # ====================================================

        if not phoenix_instance_lock.acquired():

            raise RuntimeError(
                "RESTORE_LIVE_LOCK_REQUIRED"
            )


        # ====================================================
        # INTERRUPTED RESTORE
        # ====================================================

        if store.has_in_progress():

            return {
                "success":
                    False,

                "status":
                    "RESTORE_IN_PROGRESS_BLOCKED",

                "safe_state":
                    False,

                "write_performed":
                    False,

                "in_progress_removed":
                    False,
            }


        request = (
            store.read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "safe_state":
                    True,

                "write_performed":
                    False,

                "in_progress_removed":
                    False,
            }


        # ====================================================
        # HARD SAFETY SWITCH
        # ====================================================

        if not LIVE_RESTORE_ENABLED:

            return {
                "success":
                    False,

                "status":
                    "LIVE_RESTORE_DISABLED",

                "safe_state":
                    True,

                "write_performed":
                    False,

                "pending_removed":
                    False,

                "in_progress_removed":
                    False,
            }


        # ====================================================
        # PREPARE EVERYTHING BEFORE CLAIM
        # ====================================================

        prepared = (
            self.prepare_transaction_snapshot_pending(
                request_store=
                    store,

                staging_root=
                    staging_root,
            )
        )


        transaction = prepared[
            "transaction"
        ]

        snapshot = prepared[
            "snapshot"
        ]


        # ====================================================
        # ATOMIC CLAIM
        # ====================================================
        #
        # À partir de ce moment, une panne provoque un
        # RESTORE_IN_PROGRESS au prochain démarrage.
        # ====================================================

        claimed = (
            store.claim_pending()
        )


        if (
            claimed is None
            or
            claimed.get(
                "request_id"
            )
            !=
            request.get(
                "request_id"
            )
        ):

            raise RuntimeError(
                "RESTORE_ATOMIC_CLAIM_MISMATCH"
            )


        # ====================================================
        # ACTIVE EXECUTION
        # ====================================================

        try:

            execution = (
                isolated_transaction_executor
                .execute_live(
                    transaction=
                        transaction,

                    snapshot=
                        snapshot,
                )
            )


        except Exception as error:

            try:

                journal = (
                    store.write_result(
                        request=
                            claimed,

                        status=
                            "LIVE_RESTORE_CRITICAL_FAILURE",

                        success=
                            False,

                        details={
                            "engine_status":
                                "EXECUTION_EXCEPTION",

                            "error":
                                type(
                                    error
                                ).__name__,

                            "message":
                                str(
                                    error
                                ),
                        },
                    )
                )

            except Exception:

                journal = None


            # IN_PROGRESS est volontairement conservé.
            return {
                "success":
                    False,

                "status":
                    "LIVE_RESTORE_CRITICAL_FAILURE",

                "safe_state":
                    False,

                "write_performed":
                    True,

                "in_progress_removed":
                    False,

                "request_id":
                    claimed[
                        "request_id"
                    ],

                "journal":
                    journal,
            }


        return (
            self._finalize_live_result(
                store=
                    store,

                request=
                    claimed,

                transaction=
                    transaction,

                execution=
                    execution,
            )
        )


live_restore_processor = (
    LiveRestoreProcessor()
)
