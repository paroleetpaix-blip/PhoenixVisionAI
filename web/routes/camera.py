"""
========================================================
PHOENIX VISION AI

Enterprise Camera Routes

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

from core import runtime

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

    session = session_manager.get(
        token
    )

    if session is None:

        return None

    return session


def login_redirect():

    return RedirectResponse(
        "/login",
        status_code=302
    )


@router.get(
    "/cameras",
    response_class=HTMLResponse
)
async def cameras_console(
    request: Request
):

    session = get_valid_session(
        request
    )

    if session is None:

        return login_redirect()

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
        "web/templates/cameras_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@router.get(
    "/api/cameras"
)
async def cameras_api(
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

    engine = getattr(
        runtime,
        "engine",
        None
    )

    if engine is None:

        return {
            "success": True,
            "engine_available": False,
            "total": 0,
            "online": 0,
            "offline": 0,
            "connecting": 0,
            "cameras": []
        }

    manager = getattr(
        engine,
        "camera_manager",
        None
    )

    if manager is None:

        return {
            "success": True,
            "engine_available": True,
            "camera_manager_available": False,
            "total": 0,
            "online": 0,
            "offline": 0,
            "connecting": 0,
            "cameras": []
        }

    cameras = []

    for camera in manager.get_all():

        try:

            camera_data = camera.to_dict()

        except Exception:

            continue

        cameras.append(
            camera_data
        )

    online = sum(
        1
        for camera in cameras
        if camera.get("status") == "ONLINE"
    )

    offline = sum(
        1
        for camera in cameras
        if camera.get("status") == "OFFLINE"
    )

    connecting = sum(
        1
        for camera in cameras
        if camera.get("status") == "CONNECTING"
    )

    return {
        "success": True,
        "engine_available": True,
        "camera_manager_available": True,
        "total": len(cameras),
        "online": online,
        "offline": offline,
        "connecting": connecting,
        "cameras": cameras
    }


@router.get(
    "/camera/{camera_name}",
    response_class=HTMLResponse
)
async def camera_view(
    request: Request,
    camera_name: str
):

    session = get_valid_session(
        request
    )

    if session is None:

        return login_redirect()

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
        "web/templates/camera_view.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return html.replace(
        "{{CAMERA_NAME}}",
        camera_name
    )
