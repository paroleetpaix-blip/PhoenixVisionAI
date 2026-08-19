"""
========================================================
PHOENIX VISION AI

Enterprise Alert Routes

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

from core.intelligence.intelligence_center import (
    intelligence_center
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
    "/alerts",
    response_class=HTMLResponse
)
async def alerts_console(
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
        "web/templates/alerts_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@router.get(
    "/api/alerts"
)
async def alerts_api(
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


    alerts = []


    for alert in intelligence_center.recent(
        limit
    ):

        alerts.append(
            alert.to_dict()
        )


    stats = (
        intelligence_center.stats()
    )


    return {

        "success":
            True,

        "total":
            stats["total"],

        "open":
            stats["open"],

        "high":
            stats["high"],

        "critical":
            stats["critical"],

        "acknowledged":
            stats["acknowledged"],

        "alerts":
            alerts

    }


@router.post(
    "/api/alerts/{alert_uuid}/acknowledge"
)
async def acknowledge_alert(
    alert_uuid: str,
    request: Request
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


    alert = (
        intelligence_center
        .acknowledge(
            alert_uuid
        )
    )


    if alert is None:

        return JSONResponse(
            {
                "success": False,
                "error": "ALERT_NOT_FOUND"
            },
            status_code=404
        )


    return {

        "success":
            True,

        "alert":
            alert.to_dict()

    }
