"""
========================================================
PHOENIX VISION AI

Plaques / LAPI
API Enterprise

Phoenix Security Technologies
========================================================
"""

import re

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

from core.database.history_database import (
    history_database
)

from core.security.permissions import (
    session_has_permission
)

from core.security.session import (
    session_manager
)

from core.watchlist.watchlist_database import (
    watchlist_database
)

from web.routes.enterprise import (
    user_requires_password_change
)


router = APIRouter()


WATCHLIST_CATEGORY_LABELS = {

    "STOLEN":
        "VÉHICULE VOLÉ",

    "WANTED":
        "VÉHICULE RECHERCHÉ",

    "SUSPICIOUS":
        "VÉHICULE À SURVEILLER",

    "SECURITY":
        "SIGNALEMENT DE SÉCURITÉ",

}


WATCHLIST_PRIORITY_LABELS = {

    "LOW":
        "FAIBLE",

    "MEDIUM":
        "NORMALE",

    "HIGH":
        "HAUTE",

    "CRITICAL":
        "CRITIQUE",

}


WATCHLIST_STATUS_LABELS = {

    "PENDING":
        "EN ATTENTE",

    "ACTIVE":
        "ACTIVE",

    "EXPIRED":
        "EXPIRÉE",

    "REJECTED":
        "REJETÉE",

}


STATUS_LABELS = {

    "VALIDATED":
        "VALIDÉE",

    "LOW_CONFIDENCE":
        "CONFIANCE FAIBLE",

    "INVALID_TEXT":
        "TEXTE INVALIDE",

    "OCR_EMPTY":
        "AUCUN TEXTE LU",

    "OCR_UNAVAILABLE":
        "MOTEUR OCR INDISPONIBLE",

    "PLATE_REGION_NOT_FOUND":
        "ZONE DE PLAQUE NON TROUVÉE",

    "PREPROCESS_FAILED":
        "PRÉTRAITEMENT ÉCHOUÉ",

    "NOT_DETECTED":
        "NON DÉTECTÉE",

    "INVALID_FRAME":
        "IMAGE INVALIDE",

    "INVALID_BBOX":
        "ZONE VÉHICULE INVALIDE",

    "INVALID_VEHICLE_CROP":
        "IMAGE VÉHICULE INVALIDE",

}


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


def normalize_plate_query(
    value
):

    value = str(
        value or ""
    ).upper()


    return re.sub(
        r"[^A-Z0-9]",
        "",
        value
    )


def localized_status(
    status
):

    status = str(
        status or "NOT_DETECTED"
    ).upper()


    return STATUS_LABELS.get(
        status,
        status
    )


def serialize_record(
    record
):

    if record is None:

        return None


    data = dict(
        record
    )


    data[
        "plate_status_label"
    ] = localized_status(
        data.get(
            "plate_status"
        )
    )


    return data




@router.get(
    "/plaques",
    response_class=HTMLResponse
)
async def plates_console(
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


    if not session_has_permission(
        session,
        "anpr.view"
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
                    Vous ne disposez pas de la permission
                    nécessaire pour consulter le module LAPI.
                </p>
            </body>
            </html>
            """,
            status_code=403
        )


    with open(
        "web/templates/plates_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


@router.get(
    "/api/anpr"
)
async def anpr_api(
    request: Request,
    limit: int = 100
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


    if not session_has_permission(
        session,
        "anpr.view"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    engine = getattr(
        runtime,
        "engine",
        None
    )


    ocr_available = False

    minimum_confidence = None

    validation_confidence = None

    interval_frames = None


    if engine is not None:

        reader = getattr(
            engine,
            "plate_reader",
            None
        )


        if reader is not None:

            ocr_available = bool(
                reader.is_available()
            )

            minimum_confidence = getattr(
                reader,
                "min_confidence",
                None
            )


        validation_confidence = getattr(
            engine,
            "anpr_validation_confidence",
            None
        )

        interval_frames = getattr(
            engine,
            "anpr_interval_frames",
            None
        )


    stats = (
        history_database
        .anpr_stats()
    )


    recent = (

        history_database
        .anpr_recent(
            limit=limit
        )

    )


    return {

        "success":
            True,

        "engine": {

            "available":
                engine is not None,

            "ocr_available":
                ocr_available,

            "minimum_confidence":
                minimum_confidence,

            "validation_confidence":
                validation_confidence,

            "interval_frames":
                interval_frames,

        },

        "stats":
            stats,

        "records": [

            serialize_record(
                record
            )

            for record in recent

        ]

    }


@router.get(
    "/api/anpr/search"
)
async def anpr_search_api(
    request: Request,
    plate: str = ""
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


    if not session_has_permission(
        session,
        "anpr.search"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    normalized = (
        normalize_plate_query(
            plate
        )
    )


    if len(normalized) < 3:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_PLATE_QUERY"
            },
            status_code=400
        )


    rows = (
        history_database
        .find_by_plate(
            normalized
        )
    )


    records = [

        serialize_record(
            history_database
            .row_to_dict(
                row
            )
        )

        for row in rows

    ]


    return {

        "success":
            True,

        "query":
            plate,

        "normalized":
            normalized,

        "total":
            len(
                records
            ),

        "records":
            records

    }


@router.get(
    "/api/anpr/record/{vehicle_uuid}"
)
async def anpr_record_api(
    vehicle_uuid: str,
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


    if not session_has_permission(
        session,
        "anpr.view"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    row = history_database.find_by_uuid(
        vehicle_uuid
    )


    if row is None:

        return JSONResponse(
            {
                "success": False,
                "error": "RECORD_NOT_FOUND"
            },
            status_code=404
        )


    record = history_database.row_to_dict(
        row
    )


    return {

        "success":
            True,

        "record":
            serialize_record(
                record
            )

    }


@router.get(
    "/api/anpr/forensic"
)
async def anpr_forensic_api(
    request: Request,
    plate: str = ""
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


    if not session_has_permission(
        session,
        "anpr.search"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    normalized = normalize_plate_query(
        plate
    )


    if len(normalized) < 3:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_PLATE_QUERY"
            },
            status_code=400
        )


    forensic = (
        history_database
        .plate_forensic(
            normalized
        )
    )


    records = [

        serialize_record(
            record
        )

        for record in forensic[
            "records"
        ]

    ]


    summary = {

        key:
            value

        for key, value
        in forensic.items()

        if key != "records"

    }


    return {

        "success":
            True,

        "query":
            plate,

        "normalized":
            normalized,

        "found":
            summary[
                "occurrences"
            ] > 0,

        "summary":
            summary,

        "records":
            records

    }


# ========================================================
# LISTE DE SURVEILLANCE LOCALE
# ========================================================


def serialize_watchlist_entry(
    entry
):

    if entry is None:

        return None


    data = dict(
        entry
    )


    category = str(
        data.get(
            "category"
        )
        or ""
    ).upper()


    priority = str(
        data.get(
            "priority"
        )
        or ""
    ).upper()


    status = str(
        data.get(
            "status"
        )
        or ""
    ).upper()


    data[
        "category_label"
    ] = WATCHLIST_CATEGORY_LABELS.get(
        category,
        category
    )


    data[
        "priority_label"
    ] = WATCHLIST_PRIORITY_LABELS.get(
        priority,
        priority
    )


    data[
        "status_label"
    ] = WATCHLIST_STATUS_LABELS.get(
        status,
        status
    )


    return data


@router.get(
    "/api/watchlist"
)
async def watchlist_list_api(
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


    if not session_has_permission(
        session,
        "watchlist.view"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    watchlist_database.expire_due()


    records = (
        watchlist_database
        .recent(
            limit=limit
        )
    )


    return {

        "success":
            True,

        "total":
            len(
                records
            ),

        "records": [

            serialize_watchlist_entry(
                entry
            )

            for entry in records

        ]

    }


@router.get(
    "/api/watchlist/{entry_uuid}"
)
async def watchlist_record_api(
    entry_uuid: str,
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


    if not session_has_permission(
        session,
        "watchlist.view"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    entry = (
        watchlist_database
        .find_by_uuid(
            entry_uuid
        )
    )


    if entry is None:

        return JSONResponse(
            {
                "success": False,
                "error": "WATCHLIST_ENTRY_NOT_FOUND"
            },
            status_code=404
        )


    return {

        "success":
            True,

        "record":
            serialize_watchlist_entry(
                entry
            )

    }


@router.get(
    "/api/watchlist/{entry_uuid}/audit"
)
async def watchlist_audit_api(
    entry_uuid: str,
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


    if not session_has_permission(
        session,
        "watchlist.view"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    entry = (
        watchlist_database
        .find_by_uuid(
            entry_uuid
        )
    )


    if entry is None:

        return JSONResponse(
            {
                "success": False,
                "error": "WATCHLIST_ENTRY_NOT_FOUND"
            },
            status_code=404
        )


    audit = (
        watchlist_database
        .audit_for_entry(
            entry_uuid
        )
    )


    return {

        "success":
            True,

        "entry_uuid":
            entry_uuid,

        "events":
            audit

    }


@router.post(
    "/api/watchlist/propose"
)
async def watchlist_propose_api(
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


    if not session_has_permission(
        session,
        "watchlist.propose"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    try:

        payload = await request.json()

    except Exception:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_JSON"
            },
            status_code=400
        )


    plate = normalize_plate_query(
        payload.get(
            "plate"
        )
    )


    category = str(
        payload.get(
            "category"
        )
        or ""
    ).upper()


    priority = str(
        payload.get(
            "priority"
        )
        or "MEDIUM"
    ).upper()


    reason = str(
        payload.get(
            "reason"
        )
        or ""
    ).strip()


    case_reference = str(
        payload.get(
            "case_reference"
        )
        or ""
    ).strip()


    authority = str(
        payload.get(
            "authority"
        )
        or ""
    ).strip()


    valid_from = (
        payload.get(
            "valid_from"
        )
        or None
    )


    valid_until = (
        payload.get(
            "valid_until"
        )
        or None
    )


    allowed_categories = {
        "STOLEN",
        "WANTED",
        "SUSPICIOUS",
        "SECURITY",
    }


    allowed_priorities = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }


    if len(plate) < 3:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_PLATE"
            },
            status_code=400
        )


    if category not in allowed_categories:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_CATEGORY"
            },
            status_code=400
        )


    if priority not in allowed_priorities:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_PRIORITY"
            },
            status_code=400
        )


    if len(reason) < 5:

        return JSONResponse(
            {
                "success": False,
                "error": "REASON_REQUIRED"
            },
            status_code=400
        )


    username = str(
        session.get(
            "username"
        )
        or "UNKNOWN"
    )


    role = str(
        session.get(
            "role"
        )
        or ""
    )


    try:

        entry = (
            watchlist_database
            .propose(

                plate=plate,

                category=category,

                priority=priority,

                reason=reason,

                case_reference=(
                    case_reference
                    or None
                ),

                authority=(
                    authority
                    or None
                ),

                created_by=username,

                actor_role=role,

                valid_from=valid_from,

                valid_until=valid_until

            )
        )

    except ValueError:

        return JSONResponse(
            {
                "success": False,
                "error": "INVALID_WATCHLIST_ENTRY"
            },
            status_code=400
        )


    return {

        "success":
            True,

        "record":
            serialize_watchlist_entry(
                entry
            )

    }


@router.post(
    "/api/watchlist/{entry_uuid}/approve"
)
async def watchlist_approve_api(
    entry_uuid: str,
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


    if not session_has_permission(
        session,
        "watchlist.approve_local"
    ):

        return JSONResponse(
            {
                "success": False,
                "error": "FORBIDDEN"
            },
            status_code=403
        )


    entry = (
        watchlist_database
        .find_by_uuid(
            entry_uuid
        )
    )


    if entry is None:

        return JSONResponse(
            {
                "success": False,
                "error": "WATCHLIST_ENTRY_NOT_FOUND"
            },
            status_code=404
        )


    username = str(
        session.get(
            "username"
        )
        or "UNKNOWN"
    )


    role = str(
        session.get(
            "role"
        )
        or ""
    )


    approved = (
        watchlist_database
        .approve(

            entry_uuid,

            approved_by=
                username,

            actor_role=
                role

        )
    )


    if approved is None:

        return JSONResponse(
            {
                "success": False,
                "error": "WATCHLIST_ENTRY_NOT_PENDING"
            },
            status_code=409
        )


    return {

        "success":
            True,

        "record":
            serialize_watchlist_entry(
                approved
            )

    }


@router.get(
    "/api/watchlist/capabilities/me"
)
async def watchlist_capabilities_api(
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


    return {

        "success":
            True,

        "capabilities": {

            "match":
                session_has_permission(
                    session,
                    "watchlist.match"
                ),

            "view":
                session_has_permission(
                    session,
                    "watchlist.view"
                ),

            "propose":
                session_has_permission(
                    session,
                    "watchlist.propose"
                ),

            "approve_local":
                session_has_permission(
                    session,
                    "watchlist.approve_local"
                )

        }

    }
