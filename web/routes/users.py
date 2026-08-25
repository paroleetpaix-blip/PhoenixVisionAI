from pathlib import Path

import html

"""
============================================================
PHOENIX VISION AI

Enterprise Users API

Temporary local administration layer.
Authoritative long-term administration will move to
Phoenix Admin.

Phoenix Security Technologies
============================================================
"""

from fastapi import (
    APIRouter,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response,
)


from core.security.permissions import (
    has_permission,
    session_has_permission,
)

from core.security.permission_catalog import (
    permission_catalog,
)

from core.security.session import (
    session_manager,
)

from core.users_registry.user_access import (
    user_admin_capabilities,
)

from core.users_registry.user_service import (
    UserRegistryError,
    user_registry_service,
)


from web.routes.enterprise import (
    user_requires_password_change,
)


from reportlab.graphics import (
    renderSVG,
)

from reportlab.graphics.barcode.qr import (
    QrCodeWidget,
)

from reportlab.graphics.shapes import (
    Drawing,
)


router = APIRouter()


SENSITIVE_USER_FIELDS = {
    "sexe",
    "date_naissance",
    "email",
    "telephone",
    "matricule",
    "responsable",
}


def current_session(
    request,
):

    token = request.cookies.get(
        "phoenix_token"
    )


    if not token:

        return None


    return session_manager.get(
        token
    )


def unauthorized():

    return JSONResponse(
        status_code=401,
        content={
            "success":
                False,

            "message":
                "Authentification requise.",
        },
    )


def forbidden():

    return JSONResponse(
        status_code=403,
        content={
            "success":
                False,

            "message":
                "Autorisation insuffisante.",
        },
    )


def user_payload(
    user,
    *,
    include_sensitive,
):

    if not user:

        return None


    excluded = set()


    result = {
        key:
            value

        for key, value
        in user.items()

        if key not in excluded
    }


    if not include_sensitive:

        for field in SENSITIVE_USER_FIELDS:

            result.pop(
                field,
                None,
            )


    return result


def effective_permissions(
    role,
):

    catalog = permission_catalog()

    return [
        {
            "permission":
                permission,

            "label":
                label,
        }

        for permission, label
        in catalog.items()

        if has_permission(
            role,
            permission,
        )
    ]


def registry_error_response(
    error,
):

    status_code = 400


    if error.code == "USER_NOT_FOUND":

        status_code = 404


    elif error.code in {
        "ADMIN_ACCOUNT_PROTECTED",
        "SELF_ACTION_RESTRICTED",
        "SELF_ROLE_CHANGE_RESTRICTED",
        "ADMIN_PROMOTION_RESTRICTED",
        "ADMIN_ROLE_PROTECTED",
        "PERMISSION_DENIED",
    }:

        status_code = 403


    elif error.code in {
        "ACCOUNT_EXPIRED",
        "ROLE_UNCHANGED",
    }:

        status_code = 409


    return JSONResponse(
        status_code=
            status_code,
        content={
            "success":
                False,

            "error":
                error.code,

            "message":
                error.message,
        },
    )


# ============================================================
# USERS CONSOLE
# ============================================================

@router.get(
    "/users",
    response_class=HTMLResponse,
)
async def users_console(
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return RedirectResponse(
            "/login",
            status_code=302,
        )


    username = str(
        session.get(
            "username"
        )
        or
        ""
    ).strip()


    if user_requires_password_change(
        username
    ):

        return RedirectResponse(
            "/change-password",
            status_code=302,
        )


    if not session_has_permission(
        session,
        "users.view",
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302,
        )


    template = Path(
        "web/templates/users_enterprise.html"
    )


    return template.read_text(
        encoding="utf-8"
    )


# ============================================================
# OFFICIAL USER SHEET
# ============================================================

@router.get(
    "/users/{username}/print",
    response_class=HTMLResponse,
)
async def user_print_page(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return RedirectResponse(
            "/login",
            status_code=302,
        )


    if not session_has_permission(
        session,
        "users.print",
    ):

        return RedirectResponse(
            "/users",
            status_code=302,
        )


    user = (
        user_registry_service
        .get_user(
            username
        )
    )


    if user is None:

        return HTMLResponse(
            "Utilisateur introuvable.",
            status_code=404,
        )


    try:

        user_registry_service.record_user_sheet_print(
            username,
            actor_username=
                session.get(
                    "username"
                ),
            actor_role=
                session.get(
                    "role"
                ),
        )

    except Exception as error:

        print(
            "Phoenix User Sheet audit warning:",
            type(
                error
            ).__name__,
        )


    template = Path(
        "web/templates/users_print.html"
    ).read_text(
        encoding="utf-8"
    )


    template = template.replace(
        "__PHOENIX_USERNAME__",
        html.escape(
            username,
            quote=True,
        ),
    )


    return HTMLResponse(
        template
    )


# ============================================================
# INTERNAL QR
# ============================================================

@router.get(
    "/api/users/{username}/qr.svg"
)
async def user_qr(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.print",
    ):

        return forbidden()


    user = (
        user_registry_service
        .get_user(
            username
        )
    )


    if user is None:

        return JSONResponse(
            status_code=404,
            content={
                "success":
                    False,

                "message":
                    "Utilisateur introuvable.",
            },
        )


    user_id = str(
        user.get(
            "user_id"
        )
        or
        ""
    ).strip()


    if not user_id:

        return JSONResponse(
            status_code=409,
            content={
                "success":
                    False,

                "message":
                    "Référence utilisateur indisponible.",
            },
        )


    payload = (
        "PHX-USER:"
        +
        user_id
    )


    qr = QrCodeWidget(
        payload
    )


    size = 120


    qr.barWidth = size
    qr.barHeight = size


    drawing = Drawing(
        size,
        size,
    )

    drawing.add(
        qr
    )


    svg = renderSVG.drawToString(
        drawing
    )


    if isinstance(
        svg,
        bytes,
    ):

        content = svg

    else:

        content = svg.encode(
            "utf-8"
        )


    return Response(
        content=
            content,
        media_type=
            "image/svg+xml",
        headers={
            "Cache-Control":
                "no-store",
        },
    )


# ============================================================
# CAPABILITIES
# ============================================================

@router.get(
    "/api/users/capabilities"
)
async def users_capabilities(
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    return {
        "success":
            True,

        "capabilities":
            user_admin_capabilities(
                session.get(
                    "role"
                )
            ),
    }


# ============================================================
# LIST
# ============================================================

@router.get(
    "/api/users"
)
async def users_list(
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.view",
    ):

        return forbidden()


    include_sensitive = (
        session_has_permission(
            session,
            "users.view_sensitive",
        )
    )


    users = (
        user_registry_service
        .list_users()
    )


    return {
        "success":
            True,

        "count":
            len(
                users
            ),

        "users": [
            user_payload(
                user,
                include_sensitive=
                    include_sensitive,
            )
            for user
            in users
        ],
    }


# ============================================================
# ACCOUNT REQUESTS SUMMARY
# ============================================================

@router.get(
    "/api/users/account-requests/summary"
)
async def account_requests_summary(
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.approve_request",
    ):

        return forbidden()


    return {
        "success":
            True,

        "summary":
            user_registry_service
            .account_request_summary(),
    }


# ============================================================
# USER DETAILS
# ============================================================

@router.get(
    "/api/users/{username}"
)
async def user_details(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.view",
    ):

        return forbidden()


    user = (
        user_registry_service
        .get_user(
            username
        )
    )


    if user is None:

        return JSONResponse(
            status_code=404,
            content={
                "success":
                    False,

                "message":
                    "Utilisateur introuvable.",
            },
        )


    return {
        "success":
            True,

        "user":
            user_payload(
                user,
                include_sensitive=
                    session_has_permission(
                        session,
                        "users.view_sensitive",
                    ),
            ),

        "effective_permissions":
            effective_permissions(
                user.get(
                    "role"
                )
            ),
    }


# ============================================================
# AUDIT
# ============================================================

@router.get(
    "/api/users/{username}/audit"
)
async def user_audit(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.view_audit",
    ):

        return forbidden()


    user = (
        user_registry_service
        .get_user(
            username
        )
    )


    if user is None:

        return JSONResponse(
            status_code=404,
            content={
                "success":
                    False,

                "message":
                    "Utilisateur introuvable.",
            },
        )


    events = (
        user_registry_service
        .audit_for_user(
            username
        )
    )


    return {
        "success":
            True,

        "username":
            username,

        "count":
            len(
                events
            ),

        "events":
            events,

        "integrity_valid":
            user_registry_service
            .database
            .verify_audit_chain(),
    }


# ============================================================
# EDIT DOSSIER
# ============================================================

@router.patch(
    "/api/users/{username}"
)
async def update_user(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.edit",
    ):

        return forbidden()


    try:

        payload = await request.json()

    except Exception:

        payload = {}


    if not isinstance(
        payload,
        dict,
    ):

        payload = {}


    try:

        result = (
            user_registry_service
            .update_profile(
                username,
                payload,
                actor_username=
                    session.get(
                        "username"
                    ),
                actor_role=
                    session.get(
                        "role"
                    ),
                reason=
                    "Modification administrative du dossier utilisateur",
            )
        )


    except UserRegistryError as error:

        return registry_error_response(
            error
        )


    return {
        "success":
            True,

        **result,
    }


# ============================================================
# SUSPEND
# ============================================================

@router.post(
    "/api/users/{username}/suspend"
)
async def suspend_user(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.suspend",
    ):

        return forbidden()


    try:

        payload = await request.json()

    except Exception:

        payload = {}


    try:

        result = (
            user_registry_service
            .suspend_user(
                username,
                actor_username=
                    session.get(
                        "username"
                    ),
                actor_role=
                    session.get(
                        "role"
                    ),
                reason=
                    payload.get(
                        "reason"
                    ),
            )
        )


    except UserRegistryError as error:

        return registry_error_response(
            error
        )


    revoked = (
        session_manager
        .remove_by_username(
            username
        )
    )


    return {
        "success":
            True,

        "result":
            result,

        "revoked_sessions":
            revoked,
    }


# ============================================================
# DISABLE
# ============================================================

@router.post(
    "/api/users/{username}/disable"
)
async def disable_user(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.disable",
    ):

        return forbidden()


    try:

        payload = await request.json()

    except Exception:

        payload = {}


    try:

        result = (
            user_registry_service
            .disable_user(
                username,
                actor_username=
                    session.get(
                        "username"
                    ),
                actor_role=
                    session.get(
                        "role"
                    ),
                reason=
                    payload.get(
                        "reason"
                    ),
            )
        )


    except UserRegistryError as error:

        return registry_error_response(
            error
        )


    revoked = (
        session_manager
        .remove_by_username(
            username
        )
    )


    return {
        "success":
            True,

        "result":
            result,

        "revoked_sessions":
            revoked,
    }


# ============================================================
# REACTIVATE
# ============================================================

@router.post(
    "/api/users/{username}/reactivate"
)
async def reactivate_user(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.reactivate",
    ):

        return forbidden()


    try:

        payload = await request.json()

    except Exception:

        payload = {}


    try:

        result = (
            user_registry_service
            .reactivate_user(
                username,
                actor_username=
                    session.get(
                        "username"
                    ),
                actor_role=
                    session.get(
                        "role"
                    ),
                reason=
                    payload.get(
                        "reason"
                    ),
            )
        )


    except UserRegistryError as error:

        return registry_error_response(
            error
        )


    return {
        "success":
            True,

        "result":
            result,
    }


# ============================================================
# ROLE
# ============================================================

@router.post(
    "/api/users/{username}/role"
)
async def change_user_role(
    username: str,
    request: Request,
):

    session = current_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "users.change_role",
    ):

        return forbidden()


    try:

        payload = await request.json()

    except Exception:

        payload = {}


    requested_role = str(
        payload.get(
            "role"
        )
        or
        ""
    ).strip().upper()


    try:

        result = (
            user_registry_service
            .change_role(
                username,
                requested_role,
                actor_username=
                    session.get(
                        "username"
                    ),
                actor_role=
                    session.get(
                        "role"
                    ),
                reason=
                    payload.get(
                        "reason"
                    ),
            )
        )


    except UserRegistryError as error:

        return registry_error_response(
            error
        )


    revoked = (
        session_manager
        .remove_by_username(
            username
        )
    )


    return {
        "success":
            True,

        "result":
            result,

        "revoked_sessions":
            revoked,
    }
