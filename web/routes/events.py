"""
========================================================
PHOENIX VISION AI

Enterprise Event Routes

Phoenix Security Technologies
SDK v0.6.0 Enterprise
========================================================
"""

from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse
)

from core.events.event_manager import (
    event_manager
)

from core.security.session import (
    session_manager
)

from web.routes.enterprise import (
    user_requires_password_change
)


router = APIRouter()


def get_valid_session(
    request: Request
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
    "/events",
    response_class=HTMLResponse
)
async def events_console(
    request: Request
):

    session = get_valid_session(
        request
    )


    if session is None:

        return RedirectResponse(
            "/login",
            status_code=302
        )


    username = session.get(
        "username"
    )


    if user_requires_password_change(
        username
    ):

        return RedirectResponse(
            "/change-password",
            status_code=302
        )


    with open(
        "web/templates/events_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@router.get(
    "/api/events"
)
async def events_api(
    request: Request,
    limit: int = 250
):

    session = get_valid_session(
        request
    )


    if session is None:

        return JSONResponse(
            {
                "success": False,
                "error": "UNAUTHORIZED"
            },
            status_code=401
        )


    limit = max(
        1,
        min(
            int(limit),
            1000
        )
    )


    serialized = []


    for event in event_manager.recent(
        limit
    ):

        try:

            data = event.to_dict()

        except Exception:

            continue


        serialized.append(
            data
        )


    stats = event_manager.stats()


    return {

        "success":
            True,

        "total":
            stats["total"],

        "today":
            stats["today"],

        "warnings":
            stats["warnings"],

        "critical":
            stats["critical"],

        "events":
            serialized

    }
