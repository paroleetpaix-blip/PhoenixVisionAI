"""
========================================================
PHOENIX VISION AI

Web API

Phoenix Security Technologies
========================================================
"""

from fastapi import APIRouter

from core.display.camera_grid_engine import (
    CameraGridEngine
)
from core import runtime


router = APIRouter()


# ========================================================
# LEGACY CAMERA API
# ========================================================

@router.get(
    "/api/cameras"
)
def get_cameras():

    cameras = [

        {
            "id": 1,
            "name": "Caméra 1",
            "status": "ONLINE"
        },

        {
            "id": 2,
            "name": "Caméra 2",
            "status": "ONLINE"
        },

        {
            "id": 3,
            "name": "Caméra 3",
            "status": "OFFLINE"
        },

        {
            "id": 4,
            "name": "Caméra 4",
            "status": "ONLINE"
        }

    ]


    return cameras


# ========================================================
# ENTERPRISE CAMERA GRID
# ========================================================

@router.get(
    "/api/camera-grid"
)
def camera_grid():

    cameras = []


    # ====================================================
    # CAMÉRAS RÉELLES DU PHOENIX ENGINE
    # ====================================================

    engine = runtime.engine


    if engine is not None:

        camera_manager = getattr(
            engine,
            "camera_manager",
            None
        )


        if camera_manager is not None:

            try:

                real_cameras = (
                    camera_manager
                    .get_all()
                )


                for index, camera in enumerate(
                    real_cameras,
                    start=1
                ):

                    camera_name = getattr(
                        camera,
                        "name",
                        None
                    )


                    camera_status = getattr(
                        camera,
                        "status",
                        "OFFLINE"
                    )


                    if not camera_name:

                        camera_name = (
                            f"CAM{index:02d}"
                        )


                    cameras.append({

                        "id":
                            index,

                        "name":
                            camera_name,

                        "location":
                            getattr(
                                camera,
                                "location",
                                None
                            )
                            or
                            getattr(
                                camera,
                                "source",
                                None
                            )
                            or
                            "Non renseignée",

                        "status":
                            str(
                                camera_status
                            ).upper()

                    })


            except Exception as error:

                print(
                    "[PHOENIX CAMERA API]",
                    error
                )


    # ====================================================
    # FALLBACK UI
    # ====================================================

    if not cameras:

        camera_locations = [

            "Entrée principale",

            "Parking Nord",

            "Route Nationale",

            "Portail Est",

            "Zone industrielle",

            "Entrepôt",

            "Parking Sud",

            "Rue principale",

            "Zone arrière"

        ]


        for index in range(
            1,
            10
        ):

            cameras.append({

                "id":
                    index,

                "name":
                    f"CAM{index:02d}",

                "location":
                    camera_locations[
                        index - 1
                    ],

                "status":
                    "OFFLINE"

            })


    # ====================================================
    # GRILLE
    # ====================================================

    grid_engine = (
        CameraGridEngine()
    )


    grid_engine.set_cameras(
        cameras
    )


    rows, columns = (
        grid_engine.layout()
    )


    return {

        "total":
            grid_engine.total(),

        "layout": {

            "rows":
                rows,

            "columns":
                columns

        },

        "cameras":
            grid_engine.visible_cameras()

    }

# ========================================================
# ENTERPRISE DASHBOARD SUMMARY
# ========================================================

@router.get(
    "/api/dashboard/summary"
)
def dashboard_summary():

    engine = runtime.engine


    anpr_status = "Indisponible"


    if engine is not None:

        plate_reader = getattr(
            engine,
            "plate_reader",
            None
        )


        if plate_reader is not None:

            if plate_reader.is_available():

                anpr_status = "En ligne"

            else:

                anpr_status = "OCR indisponible"

    """
    Données légères utilisées par l'interface Enterprise.

    Les événements et données véhicule seront reliés
    progressivement aux modules réels du moteur Phoenix.
    """

    return {

        "mode":
            "LIVE_UI",

        "recent_events":
            [],

        "vehicle":
            None,

        "system": {

            "ai_engine":
                "En ligne",

            "database":
                "Local",

            "anpr_server":
                anpr_status

        }

    }