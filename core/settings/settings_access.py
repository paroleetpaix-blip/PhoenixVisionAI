"""
========================================================
PHOENIX VISION AI

Enterprise Settings Access Policy

Phoenix Security Technologies
========================================================
"""

from core.security.permissions import (
    has_permission,
    normalize_role,
)

from core.settings.settings_defaults import (
    CATEGORY_ANPR,
    CATEGORY_GENERAL,
    CATEGORY_INSTALLATION,
    CATEGORY_INTERFACE,
    CATEGORY_OPERATIONS,
    CATEGORY_REPORTS,
    get_definition,
)


UPDATE_PERMISSION_BY_CATEGORY = {

    CATEGORY_GENERAL:
        "settings.update_general",

    CATEGORY_INTERFACE:
        "settings.update_interface",

    CATEGORY_OPERATIONS:
        "settings.update_operations",

    CATEGORY_ANPR:
        "settings.update_anpr",

    CATEGORY_REPORTS:
        "settings.update_reports",

    CATEGORY_INSTALLATION:
        None,

}


def can_view_settings(
    role,
):

    return has_permission(
        role,
        "settings.view",
    )


def can_view_installation(
    role,
):

    return has_permission(
        role,
        "settings.view_installation",
    )


def can_view_own_permissions(
    role,
):

    return has_permission(
        role,
        "settings.permissions.view_self",
    )


def can_view_permission_matrix(
    role,
):

    return has_permission(
        role,
        "settings.permissions.view_matrix",
    )


def can_view_settings_audit(
    role,
):

    return has_permission(
        role,
        "settings.audit.view",
    )


def update_permission_for_setting(
    setting_key,
):

    definition = get_definition(
        setting_key
    )

    if definition is None:

        return None

    return UPDATE_PERMISSION_BY_CATEGORY.get(
        definition[
            "category"
        ]
    )


def can_update_setting(
    role,
    setting_key,
):

    role = normalize_role(
        role
    )

    if role == "SYSTEM":

        return True

    definition = get_definition(
        setting_key
    )

    if definition is None:

        return False

    if not definition[
        "mutable"
    ]:

        return False

    permission = (
        update_permission_for_setting(
            setting_key
        )
    )

    if permission is None:

        return False

    return has_permission(
        role,
        permission,
    )


def editable_categories_for_role(
    role,
):

    categories = []

    for (
        category,
        permission
    ) in (
        UPDATE_PERMISSION_BY_CATEGORY
        .items()
    ):

        if permission is None:

            continue

        if has_permission(
            role,
            permission,
        ):

            categories.append(
                category
            )

    return categories


def capabilities_for_role(
    role,
):

    role = normalize_role(
        role
    )

    return {
        "role":
            role,

        "view":
            can_view_settings(
                role
            ),

        "view_installation":
            can_view_installation(
                role
            ),

        "view_own_permissions":
            can_view_own_permissions(
                role
            ),

        "view_permission_matrix":
            can_view_permission_matrix(
                role
            ),

        "view_audit":
            can_view_settings_audit(
                role
            ),

        "editable_categories":
            editable_categories_for_role(
                role
            ),

        "update_general":
            has_permission(
                role,
                "settings.update_general",
            ),

        "update_interface":
            has_permission(
                role,
                "settings.update_interface",
            ),

        "update_operations":
            has_permission(
                role,
                "settings.update_operations",
            ),

        "update_anpr":
            has_permission(
                role,
                "settings.update_anpr",
            ),

        "update_reports":
            has_permission(
                role,
                "settings.update_reports",
            ),
    }
