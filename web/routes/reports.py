"""
========================================================
PHOENIX VISION AI ENTERPRISE

Enterprise Reports API + Console

Phoenix Security Technologies
========================================================
"""

from datetime import datetime
import hashlib

from typing import (
    Any,
    Dict,
    List,
    Optional
)

from fastapi import (
    APIRouter,
    Query,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    Response
)

from pydantic import (
    BaseModel,
    Field
)

from core.reports.report_database import (
    report_database
)

from core.reports.report_service import (
    report_service
)

from core.reports.pdf_service import (
    report_pdf_service
)

from core.security.permissions import (
    session_has_permission
)

from core.security.session import (
    session_manager
)

from web.routes.enterprise import (
    user_requires_password_change
)


router = APIRouter()


class ReportGenerationRequest(
    BaseModel
):

    period_start: Optional[str] = None

    period_end: Optional[str] = None

    scope: str = "LOCAL_SITE"

    filters: Dict[str, Any] = Field(
        default_factory=dict
    )

    sections: List[str] = Field(
        default_factory=list
    )


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


def permission_denied():

    return JSONResponse(
        {
            "success": False,
            "error": "FORBIDDEN"
        },
        status_code=403
    )


def unauthorized():

    return JSONResponse(
        {
            "success": False,
            "error": "UNAUTHORIZED"
        },
        status_code=401
    )


def report_summary(
    report
):

    if not isinstance(
        report,
        dict
    ):

        return None

    return {

        "uuid":
            report.get(
                "uuid"
            ),

        "reference":
            report.get(
                "reference"
            ),

        "report_type":
            report.get(
                "report_type"
            ),

        "title":
            report.get(
                "title"
            ),

        "period_start":
            report.get(
                "period_start"
            ),

        "period_end":
            report.get(
                "period_end"
            ),

        "scope":
            report.get(
                "scope"
            ),

        "generated_by":
            report.get(
                "generated_by"
            ),

        "generated_role":
            report.get(
                "generated_role"
            ),

        "generated_at":
            report.get(
                "generated_at"
            ),

        "status":
            report.get(
                "status"
            ),

        "version":
            report.get(
                "version"
            ),

        "snapshot_hash":
            report.get(
                "snapshot_hash"
            )

    }


# =====================================================
# CONSOLE HTML
# =====================================================

@router.get(
    "/reports",
    response_class=HTMLResponse
)
async def reports_console(
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
        "reports.view"
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302
        )

    with open(
        "web/templates/reports_enterprise.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =====================================================
# CAPACITÉS
# =====================================================

@router.get(
    "/api/reports/capabilities"
)
async def reports_capabilities(
    request: Request
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    return {

        "success":
            True,

        "capabilities": {

            "view":
                session_has_permission(
                    session,
                    "reports.view"
                ),

            "generate":
                session_has_permission(
                    session,
                    "reports.generate"
                ),

            "print":
                session_has_permission(
                    session,
                    "reports.print"
                ),

            "export_pdf":
                session_has_permission(
                    session,
                    "reports.export_pdf"
                )

        }

    }


# =====================================================
# APERÇU RÉEL DE LA PÉRIODE
# =====================================================

@router.get(
    "/api/reports/preview"
)
async def reports_preview(
    request: Request,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.view"
    ):

        return permission_denied()

    try:

        snapshot = (
            report_service
            .operational_snapshot(

                start=
                    period_start,

                end=
                    period_end,

                recent_limit=
                    10
            )
        )

    except ValueError as exc:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "INVALID_PERIOD",

                "message":
                    str(
                        exc
                    )
            },
            status_code=400
        )

    return {

        "success":
            True,

        "snapshot":
            snapshot

    }


# =====================================================
# LISTE RÉCENTE
# =====================================================

@router.get(
    "/api/reports"
)
async def reports_list(
    request: Request,
    limit: int = Query(
        default=100,
        ge=1,
        le=500
    )
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.view"
    ):

        return permission_denied()

    reports = (
        report_database
        .recent(
            limit=limit
        )
    )

    return {

        "success":
            True,

        "total":
            len(
                reports
            ),

        "reports": [
            report_summary(
                report
            )
            for report in reports
        ]

    }


# =====================================================
# RECHERCHE
# =====================================================

@router.get(
    "/api/reports/search"
)
async def reports_search(
    request: Request,

    reference: Optional[str] = None,

    report_type: Optional[str] = None,

    generated_by: Optional[str] = None,

    status: Optional[str] = None,

    scope: Optional[str] = None,

    period_start: Optional[str] = None,

    period_end: Optional[str] = None,

    limit: int = Query(
        default=100,
        ge=1,
        le=500
    )
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.view"
    ):

        return permission_denied()

    reports = (
        report_database
        .search(

            reference=
                reference,

            report_type=
                report_type,

            generated_by=
                generated_by,

            status=
                status,

            scope=
                scope,

            period_start=
                period_start,

            period_end=
                period_end,

            limit=
                limit
        )
    )

    return {

        "success":
            True,

        "total":
            len(
                reports
            ),

        "reports":
            reports

    }


# =====================================================
# GÉNÉRATION
# =====================================================

@router.post(
    "/api/reports/generate"
)
async def generate_report(
    payload: ReportGenerationRequest,
    request: Request
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.generate"
    ):

        return permission_denied()

    username = str(
        session.get(
            "username"
        )
        or
        "unknown"
    )

    role = str(
        session.get(
            "role"
        )
        or
        "UNKNOWN"
    ).upper()

    sections = (
        payload.sections
        if payload.sections
        else None
    )

    try:

        report = (
            report_service
            .generate_operational_report(

                generated_by=
                    username,

                generated_role=
                    role,

                period_start=
                    payload.period_start,

                period_end=
                    payload.period_end,

                scope=
                    payload.scope,

                filters=
                    payload.filters,

                sections=
                    sections
            )
        )

    except ValueError as exc:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "INVALID_PERIOD",

                "message":
                    str(
                        exc
                    )
            },
            status_code=400
        )

    return {

        "success":
            True,

        "report":
            report

    }


# =====================================================
# DOCUMENT IMPRIMABLE
# =====================================================

@router.get(
    "/reports/{reference}/print",
    response_class=HTMLResponse
)
async def report_print_page(
    reference: str,
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


    if not session_has_permission(
        session,
        "reports.print"
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
                    Permission reports.print requise.
                </p>
            </body>
            </html>
            """,
            status_code=403
        )


    report = (
        report_database
        .find_by_reference(
            reference
        )
    )


    if report is None:

        return HTMLResponse(
            """
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <title>Rapport introuvable</title>
            </head>
            <body>
                <h1>Rapport introuvable</h1>
            </body>
            </html>
            """,
            status_code=404
        )


    with open(
        "web/templates/reports_print.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =====================================================
# DONNÉES IMPRIMABLES
# =====================================================

@router.get(
    "/api/reports/{reference}/printable"
)
async def report_printable_api(
    reference: str,
    request: Request
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "reports.print"
    ):

        return permission_denied()


    report = (
        report_database
        .find_by_reference(
            reference
        )
    )


    if report is None:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_NOT_FOUND"
            },
            status_code=404
        )


    actor = str(
        session.get(
            "username"
        )
        or
        "unknown"
    )


    role = str(
        session.get(
            "role"
        )
        or
        "UNKNOWN"
    ).upper()


    prepared_at = (
        datetime.now()
        .isoformat()
    )


    report_database.add_audit(

        report[
            "uuid"
        ],

        "PRINT_VIEWED",

        actor,

        role,

        {
            "reference":
                report[
                    "reference"
                ],

            "channel":
                "BROWSER_PRINT_VIEW"
        }
    )


    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )


    audit = (
        report_database
        .audit_for_report(
            report[
                "uuid"
            ]
        )
    )


    return {

        "success":
            True,

        "report":
            report,

        "integrity":
            integrity,

        "audit":
            audit,

        "prepared_by":
            actor,

        "prepared_role":
            role,

        "prepared_at":
            prepared_at

    }


# =====================================================
# DEMANDE D'IMPRESSION
#
# On trace une demande envoyée au navigateur.
# On ne prétend pas que l'impression physique
# a obligatoirement abouti.
# =====================================================

@router.post(
    "/api/reports/{reference}/print-requested"
)
async def report_print_requested(
    reference: str,
    request: Request
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "reports.print"
    ):

        return permission_denied()


    report = (
        report_database
        .find_by_reference(
            reference
        )
    )


    if report is None:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_NOT_FOUND"
            },
            status_code=404
        )


    actor = str(
        session.get(
            "username"
        )
        or
        "unknown"
    )


    role = str(
        session.get(
            "role"
        )
        or
        "UNKNOWN"
    ).upper()


    requested_at = (
        datetime.now()
        .isoformat()
    )


    report_database.add_audit(

        report[
            "uuid"
        ],

        "PRINT_REQUESTED",

        actor,

        role,

        {
            "reference":
                report[
                    "reference"
                ],

            "channel":
                "BROWSER_PRINT_DIALOG"
        }
    )


    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )


    audit = (
        report_database
        .audit_for_report(
            report[
                "uuid"
            ]
        )
    )


    return {

        "success":
            True,

        "requested_at":
            requested_at,

        "integrity":
            integrity,

        "audit":
            audit

    }


# =====================================================
# EXPORT PDF OFFICIEL
# =====================================================

@router.get(
    "/api/reports/{reference}/pdf"
)
async def report_pdf_export(
    reference: str,
    request: Request
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "reports.export_pdf"
    ):

        return permission_denied()


    report = (
        report_database
        .find_by_reference(
            reference
        )
    )


    if report is None:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_NOT_FOUND"
            },
            status_code=404
        )


    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )


    if not (
        integrity.get(
            "snapshot_valid"
        )
        and
        integrity.get(
            "audit_valid"
        )
    ):

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_INTEGRITY_FAILED"
            },
            status_code=409
        )


    actor = str(
        session.get(
            "username"
        )
        or
        "unknown"
    )


    role = str(
        session.get(
            "role"
        )
        or
        "UNKNOWN"
    ).upper()


    filename = (
        report[
            "reference"
        ]
        +
        ".pdf"
    )


    report_database.add_audit(

        report[
            "uuid"
        ],

        "PDF_EXPORT_REQUESTED",

        actor,

        role,

        {
            "reference":
                report[
                    "reference"
                ],

            "filename":
                filename
        }
    )


    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )


    audit = (
        report_database
        .audit_for_report(
            report[
                "uuid"
            ]
        )
    )


    try:

        pdf_bytes = (
            report_pdf_service
            .build(
                report,
                integrity,
                audit
            )
        )


    except Exception as exc:

        report_database.add_audit(

            report[
                "uuid"
            ],

            "PDF_GENERATION_FAILED",

            actor,

            role,

            {
                "error_type":
                    type(
                        exc
                    ).__name__
            }
        )


        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "PDF_GENERATION_FAILED"
            },
            status_code=500
        )


    pdf_hash = (
        hashlib.sha256(
            pdf_bytes
        )
        .hexdigest()
    )


    report_database.add_audit(

        report[
            "uuid"
        ],

        "PDF_GENERATED",

        actor,

        role,

        {
            "filename":
                filename,

            "size_bytes":
                len(
                    pdf_bytes
                ),

            "pdf_sha256":
                pdf_hash
        }
    )


    return Response(

        content=
            pdf_bytes,

        media_type=
            "application/pdf",

        headers={

            "Content-Disposition":
                (
                    'attachment; filename="'
                    +
                    filename
                    +
                    '"'
                ),

            "Cache-Control":
                "no-store",

            "X-Content-Type-Options":
                "nosniff"

        }

    )


# =====================================================
# AUDIT
# =====================================================

@router.get(
    "/api/reports/{reference}/audit"
)
async def report_audit(
    reference: str,
    request: Request
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.view"
    ):

        return permission_denied()

    report = (
        report_database
        .find_by_reference(
            reference
        )
    )

    if report is None:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_NOT_FOUND"
            },
            status_code=404
        )

    audit = (
        report_database
        .audit_for_report(
            report[
                "uuid"
            ]
        )
    )

    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )

    return {

        "success":
            True,

        "reference":
            report[
                "reference"
            ],

        "integrity":
            integrity,

        "audit":
            audit

    }


# =====================================================
# DÉTAIL
# Route dynamique gardée en dernier.
# =====================================================

@router.get(
    "/api/reports/{reference}"
)
async def report_detail(
    reference: str,
    request: Request
):

    session = get_valid_session(
        request
    )

    if session is None:

        return unauthorized()

    if not session_has_permission(
        session,
        "reports.view"
    ):

        return permission_denied()

    report = (
        report_database
        .find_by_reference(
            reference
        )
    )

    if report is None:

        return JSONResponse(
            {
                "success":
                    False,

                "error":
                    "REPORT_NOT_FOUND"
            },
            status_code=404
        )

    integrity = (
        report_database
        .verify_report_integrity(
            report[
                "uuid"
            ]
        )
    )

    return {

        "success":
            True,

        "report":
            report,

        "integrity":
            integrity

    }
