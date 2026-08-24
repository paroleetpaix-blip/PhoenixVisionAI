"""
========================================================
PHOENIX VISION AI

ANPR Human Review Policy

Phoenix Security Technologies
========================================================
"""

from core.settings.settings_service import (
    settings_service,
)


UNCERTAIN_STATUSES = {
    "LOW_CONFIDENCE",
    "INVALID_TEXT",
}


def review_uncertain_reads_enabled():

    try:

        return bool(
            settings_service.value(
                "anpr.review_uncertain_reads"
            )
        )

    except Exception:

        # Politique de sécurité :
        # en cas d'indisponibilité des Settings,
        # la vérification humaine reste active.
        return True


def requires_human_review(
    record,
    *,
    enabled=None,
):

    if enabled is None:

        enabled = (
            review_uncertain_reads_enabled()
        )

    if not enabled:

        return False


    if not isinstance(
        record,
        dict,
    ):

        return False


    status = str(
        record.get(
            "plate_status"
        )
        or
        ""
    ).strip().upper()


    return (
        status
        in
        UNCERTAIN_STATUSES
    )


def review_policy_status():

    enabled = (
        review_uncertain_reads_enabled()
    )

    return {
        "enabled":
            enabled,

        "uncertain_statuses":
            sorted(
                UNCERTAIN_STATUSES
            ),

        "meaning":
            (
                "HUMAN_REVIEW"
                if enabled
                else
                "TECHNICAL_RECORD_ONLY"
            ),
    }
