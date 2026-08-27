"""
========================================================
PHOENIX VISION AI

Enterprise Permission System

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""


ROLE_PERMISSIONS = {

    "ADMIN": {
        "*"
    },


    "SUPERVISOR": {
        "watchlist.match",
        "watchlist.view",
        "watchlist.propose",
        "watchlist.approve_local",


        "anpr.view",
        "anpr.search",


        "history.view",
        "history.print",

        "evidence.view",
        "evidence.print",
        "evidence.export_video",

        "reports.view",
        "reports.generate",
        "reports.print",
        "reports.export_pdf",

        "settings.view",
        "settings.view_installation",
        "settings.permissions.view_self",
        "settings.permissions.view_matrix",
        "settings.update_operations",
        "settings.update_anpr",
        "settings.update_reports",
        "settings.audit.view",

        # Utilisateurs — supervision en lecture
        "users.view",
        "users.view_audit",
        "users.print",

        "system.view",

    },


    "ANALYST": {
        "watchlist.match",
        "watchlist.view",
        "watchlist.propose",


        "anpr.view",
        "anpr.search",


        "history.view",
        "history.print",

        "evidence.view",

        "reports.view",
        "reports.generate",
        "reports.print",
        "reports.export_pdf",

        "settings.view",
        "settings.view_installation",
        "settings.permissions.view_self",

    },


    "OPERATOR": {
        "watchlist.match",


        "anpr.view",
        "anpr.search",


        "history.view",

        "evidence.view",

        "settings.view",
        "settings.view_installation",
        "settings.permissions.view_self",

    },

}


def normalize_role(
    role
):

    return str(
        role or ""
    ).strip().upper()


def permissions_for_role(
    role
):

    role = normalize_role(
        role
    )

    return set(
        ROLE_PERMISSIONS.get(
            role,
            set()
        )
    )


def has_permission(
    role,
    permission
):

    permissions = (
        permissions_for_role(
            role
        )
    )

    return (
        "*"
        in permissions
        or
        permission
        in permissions
    )


def session_has_permission(
    session,
    permission
):

    if not session:

        return False

    return has_permission(

        session.get(
            "role"
        ),

        permission

    )
