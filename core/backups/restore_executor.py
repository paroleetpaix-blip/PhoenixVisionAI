"""
============================================================
PHOENIX VISION AI

Restore Execution Coordinator

Phoenix Security Technologies
============================================================

Coordonne une demande Restore avec :
- le catalogue des sauvegardes ;
- le processeur OFFLINE ;
- le journal Restore ;
- la suppression contrôlée du pending.

Le processeur OFFLINE actuellement utilisé interdit
explicitement le projet Phoenix réel comme destination.
"""

from pathlib import Path

from core import constants

from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
)

from core.backups.offline_restore_processor import (
    offline_restore_processor,
)

from core.backups.restore_request import (
    validate_backup_id,
)


class RestoreExecutor:

    def __init__(
        self,
        *,
        catalog=backup_catalog,
        processor=offline_restore_processor,
    ):

        self.catalog = catalog
        self.processor = processor


    # ========================================================
    # BACKUP RESOLUTION
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
    # PREFLIGHT
    # ========================================================

    def _validate_pair(
        self,
        request,
    ):

        backup_id = (
            request[
                "backup_id"
            ]
        )

        pre_restore_id = (
            request[
                "pre_restore_backup_id"
            ]
        )


        backup = (
            self.catalog
            .get_backup(
                backup_id,
                verify_files=False,
            )
        )


        pre_restore = (
            self.catalog
            .get_backup(
                pre_restore_id,
                verify_files=False,
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
                "Backup source indisponible."
            )


        if (
            pre_restore.get(
                "status"
            )
            !=
            "AVAILABLE"
        ):

            raise RuntimeError(
                "PRE_RESTORE indisponible."
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
                "La sauvegarde de sécurité "
                "n'est pas de type PRE_RESTORE."
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
                    "Application de sauvegarde incompatible."
                )


            if (
                item.get(
                    "application_version"
                )
                !=
                current_version
            ):

                raise RuntimeError(
                    "Version de sauvegarde incompatible."
                )


        return {
            "backup":
                backup,

            "pre_restore":
                pre_restore,

            "backup_directory":
                self._backup_directory(
                    backup_id
                ),

            "pre_restore_directory":
                self._backup_directory(
                    pre_restore_id
                ),
        }


    # ========================================================
    # JOURNAL DETAILS
    # ========================================================

    @staticmethod
    def _success_details(
        result,
    ):

        verification = (
            result.get(
                "verification"
            )
            or
            {}
        )


        return {
            "files_written":
                result.get(
                    "files_written"
                ),

            "files_valid":
                verification.get(
                    "files_valid"
                ),

            "files_checked":
                verification.get(
                    "files_checked"
                ),

            "databases_valid":
                verification.get(
                    "databases_valid"
                ),

            "databases_checked":
                verification.get(
                    "databases_checked"
                ),

            "rollback_performed":
                False,
        }


    @staticmethod
    def _rollback_details(
        result,
    ):

        verification = (
            result.get(
                "rollback_verification"
            )
            or
            {}
        )


        return {
            "restore_error":
                result.get(
                    "restore_error"
                ),

            "rollback_performed":
                True,

            "rollback_files_written":
                result.get(
                    "rollback_files_written"
                ),

            "rollback_files_valid":
                verification.get(
                    "files_valid"
                ),

            "rollback_files_checked":
                verification.get(
                    "files_checked"
                ),

            "rollback_databases_valid":
                verification.get(
                    "databases_valid"
                ),

            "rollback_databases_checked":
                verification.get(
                    "databases_checked"
                ),

            "rollback_status":
                verification.get(
                    "status"
                ),
        }


    # ========================================================
    # EXECUTION
    # ========================================================

    def execute_sandbox_pending(
        self,
        *,
        request_store,
        target_root,
        simulate_failure_after=None,
        simulate_rollback_failure_after=None,
    ):

        request = (
            request_store
            .read_pending()
        )


        if request is None:

            return {
                "success":
                    False,

                "status":
                    "NO_PENDING_RESTORE",

                "safe_state":
                    True,

                "pending_removed":
                    False,
            }


        try:

            pair = (
                self._validate_pair(
                    request
                )
            )


            result = (
                self.processor
                .restore_sandbox(
                    backup_directory=
                        pair[
                            "backup_directory"
                        ],

                    pre_restore_backup_directory=
                        pair[
                            "pre_restore_directory"
                        ],

                    target_root=
                        target_root,

                    simulate_failure_after=
                        simulate_failure_after,

                    simulate_rollback_failure_after=
                        simulate_rollback_failure_after,
                )
            )


            # =================================================
            # SUCCESS
            # =================================================

            if (
                result.get(
                    "success"
                )
                and
                result.get(
                    "status"
                )
                ==
                "RESTORED"
            ):

                journal = (
                    request_store
                    .write_result(
                        request=
                            request,

                        status=
                            "RESTORED",

                        success=
                            True,

                        details=
                            self._success_details(
                                result
                            ),
                    )
                )


                request_store.remove_pending()


                return {
                    "success":
                        True,

                    "status":
                        "RESTORED",

                    "safe_state":
                        True,

                    "pending_removed":
                        True,

                    "request_id":
                        request[
                            "request_id"
                        ],

                    "result":
                        result,

                    "journal":
                        journal,
                }


            # =================================================
            # RESTORE FAILED BUT ROLLBACK VALID
            # =================================================

            rollback_verification = (
                result.get(
                    "rollback_verification"
                )
                or
                {}
            )


            if (
                result.get(
                    "status"
                )
                ==
                "ROLLED_BACK"
                and
                result.get(
                    "rollback_performed"
                )
                and
                rollback_verification.get(
                    "success"
                )
            ):

                journal = (
                    request_store
                    .write_result(
                        request=
                            request,

                        status=
                            "RESTORE_FAILED_ROLLED_BACK",

                        success=
                            False,

                        details=
                            self._rollback_details(
                                result
                            ),
                    )
                )


                # Le rollback est vérifié.
                # On retire le pending pour éviter
                # une boucle infinie au prochain boot.
                request_store.remove_pending()


                return {
                    "success":
                        False,

                    "status":
                        "RESTORE_FAILED_ROLLED_BACK",

                    "safe_state":
                        True,

                    "pending_removed":
                        True,

                    "request_id":
                        request[
                            "request_id"
                        ],

                    "result":
                        result,

                    "journal":
                        journal,
                }


            # =================================================
            # CRITICAL FAILURE
            # =================================================

            journal = (
                request_store
                .write_result(
                    request=
                        request,

                    status=
                        "RESTORE_CRITICAL_FAILURE",

                    success=
                        False,

                    details=
                        self._rollback_details(
                            result
                        ),
                )
            )


            # IMPORTANT :
            # pending conservé.
            #
            # L'état est incertain et Phoenix doit rester
            # bloqué jusqu'à intervention.
            return {
                "success":
                    False,

                "status":
                    "RESTORE_CRITICAL_FAILURE",

                "safe_state":
                    False,

                "pending_removed":
                    False,

                "request_id":
                    request[
                        "request_id"
                    ],

                "result":
                    result,

                "journal":
                    journal,
            }


        except Exception as error:

            try:

                journal = (
                    request_store
                    .write_result(
                        request=
                            request,

                        status=
                            "RESTORE_PRECHECK_FAILED",

                        success=
                            False,

                        details={
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


            # Le pending est volontairement conservé :
            # aucune restauration fiable n'a pu être exécutée.
            return {
                "success":
                    False,

                "status":
                    "RESTORE_PRECHECK_FAILED",

                "safe_state":
                    True,

                "pending_removed":
                    False,

                "request_id":
                    request.get(
                        "request_id"
                    ),

                "error":
                    type(
                        error
                    ).__name__,

                "message":
                    str(
                        error
                    ),

                "journal":
                    journal,
            }


restore_executor = (
    RestoreExecutor()
)
