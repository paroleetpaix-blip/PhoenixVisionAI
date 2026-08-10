"""
========================================================
PHOENIX VISION AI

Current Vehicle API

Phoenix Security Technologies
========================================================
"""

from fastapi import APIRouter

from core import runtime


router = APIRouter()


def safe_text(
    value,
    default="-"
):

    if value is None:

        return default


    text = str(
        value
    ).strip()


    if not text:

        return default


    return text


def safe_number(
    value,
    default=0.0
):

    try:

        return round(
            float(value),
            1
        )

    except (
        TypeError,
        ValueError
    ):

        return default


@router.get(
    "/api/current-vehicle/{camera_name}"
)
def current_vehicle(
    camera_name: str
):

    engine = runtime.engine


    # ====================================================
    # ENGINE OFF
    # ====================================================

    if engine is None:

        return {

            "available": False,

            "requested_camera":
                camera_name,

            "scope":
                "GLOBAL_TRACKER",

            "status":
                "ENGINE_OFF",

            "id":
                None,

            "uuid":
                None,

            "type":
                None,

            "plate":
                None,

            "confidence":
                0.0,

            "zone":
                None,

            "speed":
                0.0,

            "direction":
                None,

            "threat":
                None

        }


    vehicle_manager = getattr(

        engine,

        "vehicle_manager",

        None

    )


    if vehicle_manager is None:

        return {

            "available": False,

            "requested_camera":
                camera_name,

            "scope":
                "GLOBAL_TRACKER",

            "status":
                "VEHICLE_MANAGER_OFF",

            "id":
                None,

            "uuid":
                None,

            "type":
                None,

            "plate":
                None,

            "confidence":
                0.0,

            "zone":
                None,

            "speed":
                0.0,

            "direction":
                None,

            "threat":
                None

        }


    vehicle = (
        vehicle_manager
        .current_vehicle()
    )


    # ====================================================
    # AUCUN VÉHICULE ACTIF
    # ====================================================

    if vehicle is None:

        return {

            "available": False,

            "requested_camera":
                camera_name,

            "scope":
                "GLOBAL_TRACKER",

            "status":
                "NO_VEHICLE",

            "id":
                None,

            "uuid":
                None,

            "type":
                None,

            "plate":
                None,

            "confidence":
                0.0,

            "zone":
                None,

            "speed":
                0.0,

            "direction":
                None,

            "threat":
                None

        }


    # ====================================================
    # VÉHICULE RÉEL
    # ====================================================

    return {

        "available":
            True,

        # Pour le moment le VehicleManager
        # n'est pas encore séparé par caméra.

        "requested_camera":
            camera_name,

        "scope":
            "GLOBAL_TRACKER",

        "status":
            safe_text(
                getattr(
                    vehicle,
                    "status",
                    None
                ),
                "ACTIVE"
            ),

        "id":
            getattr(
                vehicle,
                "tracker_id",
                None
            ),

        "uuid":
            safe_text(
                getattr(
                    vehicle,
                    "uuid",
                    None
                ),
                None
            ),

        "type":
            safe_text(
                getattr(
                    vehicle,
                    "label",
                    None
                ),
                "Véhicule"
            ),

        "plate":
            safe_text(
                getattr(
                    vehicle,
                    "plate",
                    None
                ),
                "Non détectée"
            ),

        "plate_raw":
            safe_text(
                getattr(
                    vehicle,
                    "plate_raw",
                    None
                ),
                None
            ),

        "plate_confidence":
            safe_number(
                getattr(
                    vehicle,
                    "plate_confidence",
                    0.0
                )
            ),

        "plate_status":
            safe_text(
                getattr(
                    vehicle,
                    "plate_status",
                    None
                ),
                "NOT_DETECTED"
            ),

        "confidence":
            safe_number(
                getattr(
                    vehicle,
                    "confidence",
                    0.0
                )
                *
                100
            ),

        "zone":
            safe_text(
                getattr(
                    vehicle,
                    "zone",
                    None
                ),
                "Aucune"
            ),

        "speed":
            safe_number(
                getattr(
                    vehicle,
                    "speed",
                    0.0
                )
            ),

        "direction":
            safe_text(
                getattr(
                    vehicle,
                    "direction",
                    None
                ),
                "Inconnue"
            ),

        "threat":
            safe_text(
                getattr(
                    vehicle,
                    "threat_level",
                    None
                ),
                "NORMAL"
            )

    }