"""
============================================================
PHOENIX VISION AI

Enterprise System API

Phoenix Security Technologies
============================================================
"""

from urllib.parse import urlsplit

from fastapi import (
    APIRouter,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)

from core.security.permissions import (
    session_has_permission,
)

from core.security.session import (
    session_manager,
)

from core.system.system_health import (
    system_health_service,
)

from core.system.system_diagnostics import (
    system_diagnostics_service,
)

from web.routes.enterprise import (
    user_requires_password_change,
)


router = APIRouter()


# ============================================================
# SESSION
# ============================================================

def get_valid_session(
    request: Request,
):

    token = request.cookies.get(
        "phoenix_token"
    )

    if not token:

        return None


    return session_manager.get(
        token
    )


def request_origin_allowed(
    request: Request,
):

    host = str(
        request.headers.get(
            "host"
        )
        or
        ""
    ).strip()


    if not host:

        return False


    expected_origin = (
        f"{request.url.scheme}://"
        f"{host}"
    ).rstrip(
        "/"
    )


    origin = str(
        request.headers.get(
            "origin"
        )
        or
        ""
    ).strip().rstrip(
        "/"
    )


    if origin:

        return (
            origin
            ==
            expected_origin
        )


    referer = str(
        request.headers.get(
            "referer"
        )
        or
        ""
    ).strip()


    if referer:

        parsed = urlsplit(
            referer
        )

        referer_origin = (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
        ).rstrip(
            "/"
        )

        return (
            referer_origin
            ==
            expected_origin
        )


    # Client non navigateur :
    # le RBAC et la session restent obligatoires.
    return True


def origin_forbidden():

    return JSONResponse(
        status_code=403,
        content={
            "success":
                False,

            "error":
                "ORIGIN_FORBIDDEN",

            "message":
                (
                    "Origine de la requête "
                    "non autorisée."
                ),
        },
    )


def unauthorized():

    return JSONResponse(
        status_code=401,
        content={
            "success":
                False,

            "error":
                "UNAUTHORIZED",

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

            "error":
                "FORBIDDEN",

            "message":
                "Autorisation insuffisante.",
        },
    )


# ============================================================
# PAGE SYSTEME
# ============================================================

@router.get(
    "/system",
    response_class=HTMLResponse,
)
async def system_console(
    request: Request,
):

    session = get_valid_session(
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
        "system.view",
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302,
        )


    template = (
        "web/templates/"
        "system_enterprise.html"
    )


    try:

        with open(
            template,
            "r",
            encoding="utf-8",
        ) as file:

            return file.read()


    except FileNotFoundError:

        return HTMLResponse(
            """
            <h1>Phoenix Vision AI</h1>
            <p>
                Console Système en cours
                d'intégration.
            </p>
            """,
            status_code=200,
        )


# ============================================================
# SYSTEM HEALTH
# ============================================================

@router.get(
    "/api/system/health"
)
async def system_health(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "system.view",
    ):

        return forbidden()


    return (
        system_health_service
        .snapshot()
    )

# ============================================================
# CAPACITÉS SYSTÈME
# ============================================================

@router.get(
    "/api/system/capabilities"
)
async def system_capabilities(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "system.view",
    ):

        return forbidden()


    return {
        "success":
            True,

        "view":
            True,

        "diagnostics":
            session_has_permission(
                session,
                "system.diagnostics",
            ),

        "database_check":
            session_has_permission(
                session,
                "system.database_check",
            ),
    }


# ============================================================
# DIAGNOSTIC GÉNÉRAL
# ============================================================

@router.post(
    "/api/system/diagnostics/run"
)
async def run_system_diagnostic(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "system.diagnostics",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    username = str(
        session.get(
            "username"
        )
        or
        "UNKNOWN"
    )


    return (
        system_diagnostics_service
        .run_general(
            actor=username,
        )
    )


# ============================================================
# SQLITE QUICK CHECK
# ============================================================

@router.post(
    "/api/system/diagnostics/database-check"
)
async def run_database_check(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "system.database_check",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    try:

        payload = await request.json()

    except Exception:

        return JSONResponse(
            status_code=400,
            content={
                "success":
                    False,

                "error":
                    "INVALID_JSON",

                "message":
                    "Corps JSON invalide.",
            },
        )


    if not isinstance(
        payload,
        dict,
    ):

        return JSONResponse(
            status_code=400,
            content={
                "success":
                    False,

                "error":
                    "INVALID_REQUEST",

                "message":
                    "Requête invalide.",
            },
        )


    database_name = payload.get(
        "database"
    )


    username = str(
        session.get(
            "username"
        )
        or
        "UNKNOWN"
    )


    try:

        return (
            system_diagnostics_service
            .quick_check(
                actor=username,
                database_name=database_name,
            )
        )

    except (
        ValueError,
        FileNotFoundError,
    ) as error:

        return JSONResponse(
            status_code=400,
            content={
                "success":
                    False,

                "error":
                    "INVALID_DATABASE",

                "message":
                    str(
                        error
                    ),
            },
        )


# ============================================================
# JOURNAL DES DIAGNOSTICS
# ============================================================

@router.get(
    "/api/system/diagnostics/audit"
)
async def system_diagnostic_audit(
    request: Request,
    limit: int = 50,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "system.diagnostics",
    ):

        return forbidden()


    return {
        "success":
            True,

        "integrity":
            (
                system_diagnostics_service
                .verify_audit_chain()
            ),

        "events":
            (
                system_diagnostics_service
                .recent_events(
                    limit=limit
                )
            ),
    }
