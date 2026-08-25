"""
============================================================
PHOENIX VISION AI

Enterprise User Administration Access Policy

Phoenix Security Technologies
============================================================
"""

from core.security.permissions import (
    has_permission,
    normalize_role,
)


# Rôles opérationnels pouvant être attribués depuis
# la console temporaire Phoenix Vision AI.
VISION_AI_ASSIGNABLE_ROLES = (
    "OPERATOR",
    "ANALYST",
    "SUPERVISOR",
)


PROTECTED_ROLE = "ADMIN"


USER_ADMIN_PERMISSIONS = (
    "users.view",
    "users.view_sensitive",
    "users.edit",
    "users.approve_request",
    "users.suspend",
    "users.disable",
    "users.reactivate",
    "users.change_role",
    "users.view_audit",
    "users.print",
)


def user_admin_capabilities(
    role,
):

    normalized = normalize_role(
        role
    )


    return {
        "role":
            normalized,

        "view":
            has_permission(
                normalized,
                "users.view",
            ),

        "view_sensitive":
            has_permission(
                normalized,
                "users.view_sensitive",
            ),

        "edit":
            has_permission(
                normalized,
                "users.edit",
            ),

        "approve_request":
            has_permission(
                normalized,
                "users.approve_request",
            ),

        "suspend":
            has_permission(
                normalized,
                "users.suspend",
            ),

        "disable":
            has_permission(
                normalized,
                "users.disable",
            ),

        "reactivate":
            has_permission(
                normalized,
                "users.reactivate",
            ),

        "change_role":
            has_permission(
                normalized,
                "users.change_role",
            ),

        "view_audit":
            has_permission(
                normalized,
                "users.view_audit",
            ),

        "print":
            has_permission(
                normalized,
                "users.print",
            ),

        "assignable_roles":
            list(
                VISION_AI_ASSIGNABLE_ROLES
            )
            if has_permission(
                normalized,
                "users.change_role",
            )
            else
            [],
    }


def role_change_decision(
    actor_role,
    current_role,
    requested_role,
):

    actor = normalize_role(
        actor_role
    )

    current = normalize_role(
        current_role
    )

    requested = normalize_role(
        requested_role
    )


    if not has_permission(
        actor,
        "users.change_role",
    ):

        return {
            "allowed":
                False,

            "code":
                "PERMISSION_DENIED",

            "message":
                (
                    "Vous n'êtes pas autorisé à "
                    "modifier le rôle de cet utilisateur."
                ),
        }


    if requested == PROTECTED_ROLE:

        return {
            "allowed":
                False,

            "code":
                "ADMIN_PROMOTION_RESTRICTED",

            "message":
                (
                    "La promotion vers ADMIN est "
                    "réservée à une procédure renforcée "
                    "de Phoenix Admin."
                ),
        }


    if requested not in VISION_AI_ASSIGNABLE_ROLES:

        return {
            "allowed":
                False,

            "code":
                "INVALID_TARGET_ROLE",

            "message":
                "Le rôle demandé n'est pas autorisé.",
        }


    if current == PROTECTED_ROLE:

        return {
            "allowed":
                False,

            "code":
                "ADMIN_ROLE_PROTECTED",

            "message":
                (
                    "Le rôle d'un compte ADMIN ne peut pas "
                    "être modifié depuis Phoenix Vision AI."
                ),
        }


    if current == requested:

        return {
            "allowed":
                False,

            "code":
                "ROLE_UNCHANGED",

            "message":
                "Le rôle demandé est déjà attribué.",
        }


    return {
        "allowed":
            True,

        "code":
            "ROLE_CHANGE_ALLOWED",

        "previous_role":
            current,

        "requested_role":
            requested,
    }


def can_assign_role(
    actor_role,
    current_role,
    requested_role,
):

    return bool(
        role_change_decision(
            actor_role,
            current_role,
            requested_role,
        ).get(
            "allowed"
        )
    )
