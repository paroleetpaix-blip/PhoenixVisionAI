"""
========================================================
PHOENIX VISION AI

Enterprise History Routes

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from fastapi import APIRouter, Request

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)

from core.database.history_database import (
    history_database,
)

from core.security.session import (
    session_manager,
)

from core.security.permissions import (
    session_has_permission,
)

from web.routes.enterprise import (
    user_requires_password_change,
)


router = APIRouter()


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


@router.get(
    "/history",
    response_class=HTMLResponse,
)
async def history_console(
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


    if not session_has_permission(
        session,
        "history.view"
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302,
        )


    username = session.get(
        "username"
    )

    if user_requires_password_change(
        username
    ):

        return RedirectResponse(
            "/change-password",
            status_code=302,
        )

    with open(
        "web/templates/history_enterprise.html",
        "r",
        encoding="utf-8",
    ) as file:

        return file.read()


@router.get(
    "/api/history"
)
async def history_api(
    request: Request,
    limit: int = 500,
):

    session = get_valid_session(
        request
    )

    if session is None:

        return JSONResponse(
            {
                "success": False,
                "error": "UNAUTHORIZED",
            },
            status_code=401,
        )

    limit = max(
        1,
        min(
            int(limit),
            1000,
        ),
    )

    records = history_database.recent(
        limit
    )

    stats = history_database.stats()

    return {
        "success": True,
        "total": stats["total"],
        "today": stats["today"],
        "plates": stats["plates"],
        "threats": stats["threats"],
        "records": records,
    }


@router.get(
    "/api/history/{vehicle_uuid}"
)
async def history_detail_api(
    vehicle_uuid: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return JSONResponse(
            {
                "success": False,
                "error": "UNAUTHORIZED",
            },
            status_code=401,
        )


    row = history_database.find_by_uuid(
        vehicle_uuid
    )


    if row is None:

        return JSONResponse(
            {
                "success": False,
                "error": "HISTORY_RECORD_NOT_FOUND",
            },
            status_code=404,
        )


    record = (
        history_database.row_to_dict(
            row
        )
    )


    return {

        "success":
            True,

        "record":
            record,

        "permissions": {

            "history_print":
                session_has_permission(
                    session,
                    "history.print"
                ),

            "evidence_view":
                session_has_permission(
                    session,
                    "evidence.view"
                ),

            "evidence_print":
                session_has_permission(
                    session,
                    "evidence.print"
                ),

            "evidence_export_video":
                session_has_permission(
                    session,
                    "evidence.export_video"
                ),

        },

    }



@router.get(
    "/api/history/{vehicle_uuid}/printable"
)
async def history_printable_api(
    vehicle_uuid: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return JSONResponse(
            {
                "success": False,
                "error": "UNAUTHORIZED",
            },
            status_code=401,
        )


    if not session_has_permission(
        session,
        "history.print"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN",
                "permission": "history.print",
            },
            status_code=403,
        )


    row = history_database.find_by_uuid(
        vehicle_uuid
    )


    if row is None:

        return JSONResponse(
            {
                "success": False,
                "error": "HISTORY_RECORD_NOT_FOUND",
            },
            status_code=404,
        )


    return {

        "success":
            True,

        "record":
            history_database.row_to_dict(
                row
            ),

        "printed_by":
            session.get(
                "username"
            ),

        "role":
            session.get(
                "role"
            ),

    }


@router.get(
    "/history/{vehicle_uuid}/print",
    response_class=HTMLResponse
)
async def history_print_page(
    vehicle_uuid: str,
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


    if not session_has_permission(
        session,
        "history.print"
    ):

        return HTMLResponse(
            """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <title>Accès refusé</title>
            </head>
            <body>
                <h1>Accès refusé</h1>
                <p>
                    Permission history.print requise.
                </p>
            </body>
            </html>
            """,
            status_code=403
        )


    with open(
        "web/templates/history_print.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()
