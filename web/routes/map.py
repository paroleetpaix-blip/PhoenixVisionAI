"""
========================================================
PHOENIX VISION AI

Enterprise Operational Map Routes

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
    "/map",
    response_class=HTMLResponse
)
async def map_console(
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
        "web/templates/map_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@router.get(
    "/api/map"
)
async def map_api(
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


    cameras = []
    zones = []


    if engine is not None:

        camera_manager = getattr(
            engine,
            "camera_manager",
            None
        )


        if camera_manager is not None:

            for camera in camera_manager.get_all():

                try:

                    data = camera.to_dict()

                except Exception:

                    continue


                source = str(
                    data.get("source") or ""
                )


                if (
                    data.get("type") == "VIDEO"
                    or
                    source.lower().endswith(
                        (
                            ".mp4",
                            ".avi",
                            ".mov",
                            ".mkv"
                        )
                    )
                ):

                    source_type = "LOCAL_VIDEO"

                elif "://" in source:

                    source_type = "NETWORK_STREAM"

                else:

                    source_type = "LOCAL_DEVICE"


                cameras.append({

                    "uuid":
                        data.get("uuid"),

                    "name":
                        data.get("name"),

                    "status":
                        data.get("status"),

                    "type":
                        data.get("type"),

                    "source_type":
                        source_type,

                    "site":
                        data.get("site"),

                    "location_name":
                        data.get("location_name"),

                    "address":
                        data.get("address"),

                    "city":
                        data.get("city"),

                    "latitude":
                        data.get("latitude"),

                    "longitude":
                        data.get("longitude"),

                    "gps_configured":
                        bool(
                            data.get(
                                "gps_configured"
                            )
                        )

                })


        zone_manager = getattr(
            engine,
            "zone_manager",
            None
        )


        if zone_manager is not None:

            for zone in zone_manager.get_zones():

                try:

                    data = zone.to_dict()

                except Exception:

                    continue


                zones.append({

                    "name":
                        data.get("name"),

                    "coordinate_system":
                        "VIDEO_FRAME",

                    "x1":
                        data.get("x1"),

                    "y1":
                        data.get("y1"),

                    "x2":
                        data.get("x2"),

                    "y2":
                        data.get("y2")

                })


    online = sum(
        1
        for camera in cameras
        if camera.get("status") == "ONLINE"
    )


    connecting = sum(
        1
        for camera in cameras
        if camera.get("status") == "CONNECTING"
    )


    gps_configured = sum(
        1
        for camera in cameras
        if camera.get("gps_configured")
    )


    alert_stats = (
        intelligence_center.stats()
    )


    return {

        "success":
            True,

        "mode":
            (
                "GEOGRAPHIC"
                if gps_configured > 0
                else
                "TOPOLOGICAL"
            ),

        "geographic_mode":
            gps_configured > 0,

        "total_cameras":
            len(cameras),

        "online":
            online,

        "connecting":
            connecting,

        "gps_configured":
            gps_configured,

        "zones_total":
            len(zones),

        "open_alerts":
            alert_stats.get(
                "open",
                0
            ),

        "cameras":
            cameras,

        "zones":
            zones

    }
