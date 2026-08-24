"""
========================================================
PHOENIX VISION AI

Sensitive Actions Policy

Phoenix Security Technologies
========================================================
"""

from core.settings.settings_service import (
    settings_service,
)


SENSITIVE_ACTIONS = {

    "WATCHLIST_APPROVE": {
        "label":
            "Valider une surveillance",

        "level":
            "HIGH",
    },

    "EVIDENCE_EXPORT_VIDEO": {
        "label":
            "Exporter une vidéo de preuve",

        "level":
            "HIGH",
    },

    "REPORT_PRINT": {
        "label":
            "Imprimer un rapport officiel",

        "level":
            "MEDIUM",
    },

    "REPORT_EXPORT_PDF": {
        "label":
            "Exporter un rapport PDF",

        "level":
            "MEDIUM",
    },

}


def confirmations_enabled():

    try:

        return bool(
            settings_service.value(
                "operations.confirm_sensitive_actions"
            )
        )

    except Exception:

        # Comportement conservateur :
        # si Settings n'est pas disponible,
        # les confirmations restent actives.
        return True


def is_sensitive_action(
    action,
):

    return (
        str(
            action
            or
            ""
        ).strip().upper()
        in
        SENSITIVE_ACTIONS
    )


def requires_confirmation(
    action,
):

    return (
        confirmations_enabled()
        and
        is_sensitive_action(
            action
        )
    )


def policy_status():

    return {
        "enabled":
            confirmations_enabled(),

        "actions":
            SENSITIVE_ACTIONS,
    }
