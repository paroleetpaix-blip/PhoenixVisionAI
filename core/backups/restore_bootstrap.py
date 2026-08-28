"""
============================================================
PHOENIX VISION AI

Offline Restore Bootstrap

Phoenix Security Technologies
============================================================

IMPORTANT
---------
Ce module doit rester chargeable AVANT PhoenixServer,
PhoenixEngine, web.app et les bases SQLite globales.
"""

from core.backups.live_restore_processor import (
    LIVE_RESTORE_ENABLED,
    live_restore_processor,
)

from core.backups.restore_request import (
    restore_request_store,
)


class RestoreBootstrap:

    def __init__(
        self,
        request_store=restore_request_store,
        live_processor=live_restore_processor,
    ):

        self.request_store = (
            request_store
        )

        self.live_processor = (
            live_processor
        )


    # ========================================================
    # INSPECTION
    # ========================================================

    def inspect_pending(
        self,
    ):

        if self.request_store.has_in_progress():

            try:

                request = (
                    self.request_store
                    .read_in_progress()
                )


                return {
                    "success":
                        True,

                    "pending":
                        True,

                    "status":
                        "RESTORE_IN_PROGRESS",

                    "request":
                        request,
                }


            except Exception as error:

                return {
                    "success":
                        False,

                    "pending":
                        True,

                    "status":
                        "INVALID_RESTORE_IN_PROGRESS",

                    "error":
                        type(
                            error
                        ).__name__,

                    "message":
                        str(
                            error
                        ),
                }


        if not self.request_store.has_pending():

            return {
                "success":
                    True,

                "pending":
                    False,

                "status":
                    "NO_PENDING_RESTORE",
            }


        try:

            request = (
                self.request_store
                .read_pending()
            )


            return {
                "success":
                    True,

                "pending":
                    True,

                "status":
                    "PENDING_RESTORE",

                "request":
                    request,
            }


        except Exception as error:

            return {
                "success":
                    False,

                "pending":
                    True,

                "status":
                    "INVALID_RESTORE_REQUEST",

                "error":
                    type(
                        error
                    ).__name__,

                "message":
                    str(
                        error
                    ),
            }


    # ========================================================
    # STARTUP GATE
    # ========================================================

    def startup_gate(
        self,
    ):

        inspection = (
            self.inspect_pending()
        )


        # ====================================================
        # INTERRUPTED RESTORE
        # ====================================================

        if (
            inspection.get(
                "status"
            )
            ==
            "RESTORE_IN_PROGRESS"
        ):

            raise RuntimeError(
                "Une restauration Phoenix a été interrompue "
                "ou est encore marquée IN_PROGRESS. "
                "Démarrage bloqué par sécurité."
            )


        # ====================================================
        # NO RESTORE
        # ====================================================

        if not inspection.get(
            "pending"
        ):

            return inspection


        # ====================================================
        # INVALID REQUEST
        # ====================================================

        if not inspection.get(
            "success"
        ):

            raise RuntimeError(
                "Phoenix a détecté une demande "
                "de restauration invalide. "
                "Démarrage interrompu par sécurité."
            )


        # ====================================================
        # LIVE DISABLED — DRY RUN ONLY
        # ====================================================

        if not LIVE_RESTORE_ENABLED:

            dry_run = (
                self.live_processor
                .dry_run_pending(
                    request_store=
                        self.request_store,
                )
            )


            if not dry_run.get(
                "success"
            ):

                raise RuntimeError(
                    "Le contrôle LIVE de restauration "
                    "a échoué. "
                    "Démarrage Phoenix interrompu."
                )


            if (
                dry_run.get(
                    "write_performed"
                )
                is not False
            ):

                raise RuntimeError(
                    "Violation de sécurité Restore : "
                    "écriture inattendue pendant DRY-RUN."
                )


            raise RuntimeError(
                "Restauration Phoenix validée en DRY-RUN, "
                "mais l'écriture LIVE reste désactivée. "
                "Démarrage interrompu par sécurité."
            )


        # ====================================================
        # LIVE EXECUTION
        # ====================================================

        result = (
            self.live_processor
            .execute_pending(
                request_store=
                    self.request_store
            )
        )


        status = str(
            result.get(
                "status"
            )
            or
            ""
        )


        # Restauration réussie.
        if (
            result.get(
                "success"
            )
            and
            status
            ==
            "LIVE_RESTORE_RESTORED"
        ):

            return result


        # La restauration a échoué mais l'état exact
        # précédent a été restauré et vérifié.
        if (
            status
            ==
            "LIVE_RESTORE_FAILED_ROLLED_BACK"
            and
            result.get(
                "safe_state"
            )
            is True
        ):

            return result


        # Tout autre résultat reste bloquant.
        raise RuntimeError(
            "La restauration Phoenix n'a pas atteint "
            "un état de démarrage sûr. "
            "Démarrage interrompu."
        )


restore_bootstrap = (
    RestoreBootstrap()
)
