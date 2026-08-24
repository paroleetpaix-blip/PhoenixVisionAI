"""
========================================================
PHOENIX VISION AI ENTERPRISE

Enterprise Settings API

Phoenix Security Technologies
========================================================
"""

import platform

from core import constants

from typing import Any

from fastapi import (
    APIRouter,
    Query,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)

from pydantic import (
    BaseModel,
)

from core.i18n.locale_registry import (
    DEFAULT_LOCALE,
    public_locales,
)

from core.operations.sensitive_actions import (
    policy_status as sensitive_actions_policy_status,
)

from core.security.permission_catalog import (
    permission_label,
    public_permission_groups,
    public_security_rules,
)

from core.security.permissions import (
    ROLE_PERMISSIONS,
    has_permission,
    permissions_for_role,
    session_has_permission,
)

from core.security.session import (
    session_manager,
)

from core.settings.settings_access import (
    can_update_setting,
    can_view_permission_matrix,
    can_view_settings_audit,
    capabilities_for_role,
)

from core.settings.settings_database import (
    settings_database,
)

from core.settings.settings_defaults import (
    SETTING_DEFINITIONS,
    public_definition,
)

from core.settings.settings_service import (
    settings_service,
)


from web.routes.enterprise import (
    user_requires_password_change,
)

router = APIRouter()


# ======================================================
# REQUEST MODELS
# ======================================================

class SettingsUpdateRequest(
    BaseModel
):

    value: Any


# ======================================================
# SESSION
# ======================================================

def get_valid_session(
    request: Request,
):

    token = request.cookies.get(
        "phoenix_token"
    )

    if not token:

        return None

    if not session_manager.exists(
        token
    ):

        return None

    return session_manager.get(
        token
    )


def unauthorized():

    return JSONResponse(
        {
            "success": False,
            "error": "UNAUTHORIZED",
        },
        status_code=401,
    )


def permission_denied():

    return JSONResponse(
        {
            "success": False,
            "error": "FORBIDDEN",
        },
        status_code=403,
    )


# ======================================================
# HELPERS
# ======================================================

def session_role(
    session,
):

    return str(
        session.get(
            "role"
        )
        or
        ""
    ).strip().upper()


def session_username(
    session,
):

    return str(
        session.get(
            "username"
        )
        or
        "unknown"
    ).strip()


def permission_status_groups(
    role,
):

    groups = []

    for (
        group_key,
        group
    ) in (
        public_permission_groups()
        .items()
    ):

        entries = []

        for (
            permission,
            label
        ) in (
            group[
                "permissions"
            ]
            .items()
        ):

            entries.append(
                {
                    "permission":
                        permission,

                    "label":
                        label,

                    "allowed":
                        has_permission(
                            role,
                            permission,
                        ),
                }
            )

        groups.append(
            {
                "key":
                    group_key,

                "label":
                    group[
                        "label"
                    ],

                "permissions":
                    entries,
            }
        )

    return groups


def setting_payload(
    setting,
    role,
):

    if setting is None:

        return None

    item = dict(
        setting
    )

    item[
        "definition"
    ] = public_definition(
        setting[
            "key"
        ]
    )

    item[
        "can_update"
    ] = can_update_setting(
        role,
        setting[
            "key"
        ],
    )

    return item


def prepare_settings():

    settings_service.initialize_defaults()

    settings_service.synchronize_system_values()


# ======================================================
# SETTINGS CONSOLE
# ======================================================

@router.get(
    "/settings",
    response_class=HTMLResponse
)
async def settings_console(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return RedirectResponse(
            "/login",
            status_code=302
        )


    username = session_username(
        session
    )


    if user_requires_password_change(
        username
    ):

        return RedirectResponse(
            "/change-password",
            status_code=302
        )


    if not session_has_permission(
        session,
        "settings.view",
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302
        )


    with open(
        "web/templates/settings_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ======================================================
# OPERATIONAL SECURITY POLICY
# ======================================================

@router.get(
    "/api/settings/security-policy"
)
async def settings_security_policy(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()


    return {
        "success":
            True,

        "sensitive_actions":
            sensitive_actions_policy_status(),
    }


# ======================================================
# LANGUAGES
# ======================================================

@router.get(
    "/api/settings/languages"
)
async def settings_languages(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "settings.view",
    ):

        return permission_denied()


    return {
        "success":
            True,

        "default":
            DEFAULT_LOCALE,

        "languages":
            public_locales(),
    }


# ======================================================
# CAPABILITIES
# ======================================================

@router.get(
    "/api/settings/capabilities"
)
async def settings_capabilities(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    role = session_role(
        session
    )

    return {
        "success": True,

        "capabilities":
            capabilities_for_role(
                role
            ),
    }


# ======================================================
# ALL SETTINGS
# ======================================================

@router.get(
    "/api/settings"
)
async def settings_all(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.view",
    ):

        return permission_denied()

    prepare_settings()

    role = session_role(
        session
    )

    settings = [
        setting_payload(
            setting,
            role,
        )
        for setting
        in settings_service.all()
    ]

    stats = settings_database.stats()

    return {
        "success": True,

        "settings":
            settings,

        "stats":
            stats,
    }


# ======================================================
# DEFINITIONS
# ======================================================

@router.get(
    "/api/settings/definitions"
)
async def settings_definitions(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.view",
    ):

        return permission_denied()

    return {
        "success": True,

        "definitions":
            settings_service.definitions(),
    }


# ======================================================
# CATEGORY
# ======================================================

@router.get(
    "/api/settings/category/{category}"
)
async def settings_category(
    category: str,
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.view",
    ):

        return permission_denied()

    prepare_settings()

    category = str(
        category
        or
        ""
    ).strip().upper()

    known_categories = {
        definition[
            "category"
        ]
        for definition
        in SETTING_DEFINITIONS.values()
    }

    if category not in known_categories:

        return JSONResponse(
            {
                "success": False,
                "error": "CATEGORY_NOT_FOUND",
            },
            status_code=404,
        )

    role = session_role(
        session
    )

    settings = [
        setting_payload(
            setting,
            role,
        )
        for setting
        in settings_service.by_category(
            category
        )
    ]

    return {
        "success": True,

        "category":
            category,

        "settings":
            settings,
    }


# ======================================================
# MY PERMISSIONS
# ======================================================

@router.get(
    "/api/settings/permissions/me"
)
async def settings_permissions_me(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.permissions.view_self",
    ):

        return permission_denied()

    role = session_role(
        session
    )

    permissions = sorted(
        permissions_for_role(
            role
        )
    )

    return {
        "success": True,

        "username":
            session_username(
                session
            ),

        "role":
            role,

        "all_access":
            "*"
            in permissions,

        "permissions":
            permissions,

        "permission_labels": {
            permission:
                permission_label(
                    permission
                )
            for permission
            in permissions
            if permission != "*"
        },

        "permission_groups":
            public_permission_groups(),

        "mandatory_security_rules":
            public_security_rules(),

        "permission_status_groups":
            permission_status_groups(
                role
            ),

        "settings_capabilities":
            capabilities_for_role(
                role
            ),
    }


# ======================================================
# PERMISSION MATRIX — READ ONLY
# ======================================================

@router.get(
    "/api/settings/permissions/matrix"
)
async def settings_permission_matrix(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    role = session_role(
        session
    )

    if not can_view_permission_matrix(
        role
    ):

        return permission_denied()

    permission_catalog = sorted(
        {
            permission
            for permissions
            in ROLE_PERMISSIONS.values()
            for permission
            in permissions
            if permission != "*"
        }
    )

    role_order = [
        "ADMIN",
        "SUPERVISOR",
        "ANALYST",
        "OPERATOR",
    ]

    matrix = {}

    for current_role in role_order:

        matrix[
            current_role
        ] = {
            permission:
                has_permission(
                    current_role,
                    permission,
                )
            for permission
            in permission_catalog
        }

    return {
        "success": True,

        "read_only":
            True,

        "permissions":
            permission_catalog,

        "permission_labels": {
            permission:
                permission_label(
                    permission
                )
            for permission
            in permission_catalog
        },

        "permission_groups":
            public_permission_groups(),

        "roles":
            role_order,

        "matrix":
            matrix,
    }


# ======================================================
# INSTALLATION INFORMATION
# ======================================================

@router.get(
    "/api/settings/installation"
)
async def settings_installation(
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.view_installation",
    ):

        return permission_denied()

    prepare_settings()

    def value(
        key,
    ):

        return settings_service.value(
            key
        )

    return {
        "success": True,

        "product": {
            "name":
                constants.APP_NAME,

            "version":
                constants.VERSION,

            "codename":
                constants.CODENAME,

            "publisher":
                constants.COMPANY,

            "license":
                constants.LICENSE,

            "source":
                "core.constants",
        },

        "installation": {
            "type":
                "LOCAL",

            "management":
                "LOCAL",

            "update_management":
                "PHOENIX_CONTROL_CENTER_FUTURE",
        },

        "site": {
            "name":
                value(
                    "general.site_name"
                ),

            "country_code":
                value(
                    "general.country_code"
                ),

            "city":
                value(
                    "general.city"
                ),

            "timezone":
                value(
                    "general.timezone"
                ),
        },

        "interface": {
            "default_language":
                value(
                    "interface.default_language"
                ),

            "date_format":
                value(
                    "interface.date_format"
                ),

            "time_format":
                value(
                    "interface.time_format"
                ),
        },

        "runtime": {
            "operating_system":
                platform.system(),

            "os_release":
                platform.release(),

            "architecture":
                platform.machine(),

            "python_version":
                platform.python_version(),
        },
    }


# ======================================================
# SETTINGS AUDIT
# ======================================================

@router.get(
    "/api/settings/audit"
)
async def settings_audit(
    request: Request,

    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    role = session_role(
        session
    )

    if not can_view_settings_audit(
        role
    ):

        return permission_denied()

    prepare_settings()

    audit = settings_database.recent_audit(
        limit
    )

    integrity = (
        settings_database
        .verify_audit_chain()
    )

    return {
        "success": True,

        "integrity":
            integrity,

        "events":
            audit,
    }


# ======================================================
# UPDATE SETTING
# ======================================================

@router.put(
    "/api/settings/{setting_key}"
)
async def settings_update(
    setting_key: str,
    payload: SettingsUpdateRequest,
    request: Request,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "settings.view",
    ):

        return permission_denied()

    role = session_role(
        session
    )

    actor = session_username(
        session
    )

    if (
        setting_key
        not in SETTING_DEFINITIONS
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "SETTING_NOT_FOUND",
            },
            status_code=404,
        )

    if not can_update_setting(
        role,
        setting_key,
    ):

        return permission_denied()

    try:

        result = settings_service.update(

            setting_key,

            payload.value,

            actor=
                actor,

            actor_role=
                role,

            details={
                "channel":
                    "SETTINGS_API",
            },
        )

    except ValueError as error:

        return JSONResponse(
            {
                "success": False,

                "error":
                    "INVALID_SETTING_VALUE",

                "message":
                    str(
                        error
                    ),
            },
            status_code=422,
        )

    except PermissionError:

        return permission_denied()

    except KeyError:

        return JSONResponse(
            {
                "success": False,
                "error": "SETTING_NOT_FOUND",
            },
            status_code=404,
        )

    return {
        "success": True,

        "setting":
            setting_payload(
                result,
                role,
            ),
    }
