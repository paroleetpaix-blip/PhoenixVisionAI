"""
============================================================
PHOENIX VISION AI

Enterprise Backup API

Phoenix Security Technologies
============================================================
"""

from pathlib import Path

from datetime import (
    timedelta,
)

from core import constants

from fastapi import (
    APIRouter,
    Request,
)

from fastapi.encoders import (
    jsonable_encoder,
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)


from core.backups.backup_catalog import (
    backup_catalog,
)

from core.backups.backup_automation_policy import (
    RETENTION_DAILY_DAYS,
    RETENTION_HOURLY_HOURS,
    RETENTION_MONTHLY_MONTHS,
    RETENTION_WEEKLY_WEEKS,
)

from core.backups.backup_scheduler import (
    backup_scheduler,
)

from core.backups.backup_migration_service import (
    backup_migration_service,
)

from core.backups.backup_locks import (
    backup_mutation_lock,
)

from core.backups.backup_service import (
    BACKUP_DIRECTORY,
    backup_service,
)

from core.backups.live_restore_processor import (
    live_restore_processor,
)

from core.backups.restore_flags import (
    LIVE_RESTORE_ENABLED,
)

from core.backups.restore_request import (
    validate_backup_id,
)

from core.backups.restore_service import (
    restore_service,
)

from core.security.permissions import (
    session_has_permission,
)

from web.routes.enterprise import (
    user_requires_password_change,
)

from web.routes.system import (
    forbidden,
    get_valid_session,
    origin_forbidden,
    request_origin_allowed,
    unauthorized,
)


router = APIRouter()


# ============================================================
# JSON ERROR
# ============================================================

def api_error(
    *,
    status_code,
    status,
    message,
):

    return JSONResponse(
        status_code=
            status_code,

        content={
            "success":
                False,

            "status":
                status,

            "message":
                message,
        },
    )


# ============================================================
# SAFE JSON RESPONSE
# ============================================================

def api_response(
    payload,
    *,
    status_code=200,
):

    return JSONResponse(
        status_code=
            status_code,

        content=
            jsonable_encoder(
                payload
            ),
    )


# ============================================================
# ACTOR
# ============================================================

def session_actor(
    session,
):

    return str(
        session.get(
            "username"
        )
        or
        "UNKNOWN"
    ).strip()


# ============================================================
# BACKUP ID
# ============================================================

def validated_backup_id(
    backup_id,
):

    try:

        return validate_backup_id(
            backup_id
        )

    except Exception as error:

        raise ValueError(
            "Identifiant de sauvegarde invalide."
        ) from error


# ============================================================
# CATALOG LIST
# ============================================================

def catalog_backups():

    root = Path(
        BACKUP_DIRECTORY
    )


    if not root.exists():

        return []


    if (
        not root.is_dir()
        or
        root.is_symlink()
    ):

        raise RuntimeError(
            "Répertoire de sauvegarde invalide."
        )


    items = []


    for directory in sorted(
        root.iterdir(),
        key=lambda item:
            item.name,
        reverse=True,
    ):

        if (
            not directory.is_dir()
            or
            directory.is_symlink()
        ):

            continue


        try:

            backup_id = (
                validated_backup_id(
                    directory.name
                )
            )

        except ValueError:

            # Ignore notamment *.partial et anciens fichiers.
            continue


        try:

            item = (
                backup_catalog
                .get_backup(
                    backup_id,
                    verify_files=False,
                )
            )


            items.append(
                item
            )


        except Exception as error:

            items.append(
                {
                    "backup_id":
                        backup_id,

                    "status":
                        "INVALID",

                    "error":
                        type(
                            error
                        ).__name__,
                }
            )


    return items


# ============================================================
# PRE_RESTORE ID EXTRACTION
# ============================================================

def extract_pre_restore_backup_id(
    prepared,
):

    if not isinstance(
        prepared,
        dict,
    ):

        raise RuntimeError(
            "Résultat PRE_RESTORE invalide."
        )


    direct_keys = (
        "pre_restore_backup_id",
        "pre_restore_id",
        "safety_backup_id",
    )


    for key in direct_keys:

        value = prepared.get(
            key
        )


        if value:

            return validated_backup_id(
                value
            )


    nested_keys = (
        "pre_restore",
        "pre_restore_backup",
        "safety_backup",
    )


    for key in nested_keys:

        value = prepared.get(
            key
        )


        if isinstance(
            value,
            dict,
        ):

            candidate = (
                value.get(
                    "backup_id"
                )
                or
                value.get(
                    "id"
                )
            )


            if candidate:

                return validated_backup_id(
                    candidate
                )


        elif isinstance(
            value,
            str,
        ):

            return validated_backup_id(
                value
            )


    raise RuntimeError(
        "Identifiant PRE_RESTORE introuvable."
    )


# ============================================================
# PAGE SAUVEGARDES
# ============================================================

@router.get(
    "/backups",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def backups_console(
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
        "backups.view",
    ):

        return RedirectResponse(
            "/enterprise",
            status_code=302,
        )


    template = (
        Path("web/templates")
        /
        "backups_enterprise.html"
    )


    try:

        return template.read_text(
            encoding="utf-8"
        )


    except FileNotFoundError:

        return HTMLResponse(
            """
            <h1>Phoenix Vision AI</h1>
            <p>
                Console Sauvegardes indisponible.
            </p>
            """,
            status_code=500,
        )


# ============================================================
# AUTOMATION STATUS
# ============================================================

def backup_automation_snapshot():

    scheduler_status = (
        backup_scheduler.status()
    )


    latest = (
        backup_scheduler
        .latest_automatic()
    )


    latest_id = None

    latest_created_at = None

    next_due_at = None


    if latest:

        latest_id = latest.get(
            "backup_id"
        )

        latest_created_at = latest.get(
            "created_at"
        )


        created_at = latest.get(
            "_created_at"
        )


        if created_at is not None:

            next_due_at = (
                created_at
                +
                timedelta(
                    seconds=
                        scheduler_status[
                            "interval_seconds"
                        ]
                )
            ).isoformat()


    return {
        **scheduler_status,

        "latest_backup_id":
            latest_id,

        "latest_created_at":
            latest_created_at,

        "next_due_at":
            next_due_at,

        "retention": {
            "hourly_hours":
                RETENTION_HOURLY_HOURS,

            "daily_days":
                RETENTION_DAILY_DAYS,

            "weekly_weeks":
                RETENTION_WEEKLY_WEEKS,

            "monthly_months":
                RETENTION_MONTHLY_MONTHS,
        },
    }


# ============================================================
# CAPABILITIES
# ============================================================

@router.get(
    "/api/backups/capabilities"
)
async def backup_capabilities(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.view",
    ):

        return forbidden()


    return {
        "success":
            True,

        "view":
            True,

        "create":
            session_has_permission(
                session,
                "backups.create",
            ),

        "verify":
            session_has_permission(
                session,
                "backups.verify",
            ),

        "restore":
            session_has_permission(
                session,
                "backups.restore",
            ),

        "migrate":
            session_has_permission(
                session,
                "backups.migrate",
            ),

        "application":
            getattr(
                constants,
                "APP_NAME",
                "Phoenix Vision AI",
            ),

        "application_version":
            getattr(
                constants,
                "VERSION",
                "unknown",
            ),

        "live_restore_enabled":
            LIVE_RESTORE_ENABLED,

        "automation":
            backup_automation_snapshot(),
    }


# ============================================================
# RESTORE STATUS
#
# IMPORTANT :
# cette route doit être déclarée avant /api/backups/{backup_id}
# ============================================================

@router.get(
    "/api/backups/restore/status"
)
async def restore_status(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.restore",
    ):

        return forbidden()


    store = (
        live_restore_processor
        .request_store
    )


    try:

        if store.has_in_progress():

            restore_request = (
                store.read_in_progress()
            )

            status = (
                "RESTORE_IN_PROGRESS"
            )


        elif store.has_pending():

            restore_request = (
                store.read_pending()
            )

            status = (
                "RESTORE_PENDING"
            )


        else:

            restore_request = None

            status = (
                "IDLE"
            )


        return {
            "success":
                True,

            "status":
                status,

            "live_restore_enabled":
                LIVE_RESTORE_ENABLED,

            "request":
                restore_request,
        }


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "RESTORE_STATUS_ERROR",

            message=
                str(
                    error
                ),
        )


# ============================================================
# LIST BACKUPS
# ============================================================

@router.get(
    "/api/backups"
)
async def list_backups(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.view",
    ):

        return forbidden()


    try:

        backups = (
            catalog_backups()
        )


        return {
            "success":
                True,

            "count":
                len(
                    backups
                ),

            "backups":
                backups,
        }


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "BACKUP_CATALOG_ERROR",

            message=
                str(
                    error
                ),
        )


# ============================================================
# CREATE BACKUP
# ============================================================

@router.post(
    "/api/backups"
)
async def create_backup(
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.create",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    actor = session_actor(
        session
    )


    try:

        with backup_mutation_lock:

            result = (
                backup_service
                .create_backup(
                    actor=
                        actor,

                    backup_type=
                        "MANUAL",
                )
            )


        return api_response(
            result,
            status_code=201,
        )


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "BACKUP_CREATE_FAILED",

            message=
                str(
                    error
                ),
        )


# ============================================================
# VERIFY BACKUP
# ============================================================

@router.post(
    "/api/backups/{backup_id}/verify"
)
async def verify_backup(
    backup_id: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.verify",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    try:

        backup_id = (
            validated_backup_id(
                backup_id
            )
        )


        result = (
            backup_catalog
            .get_backup(
                backup_id,
                verify_files=True,
            )
        )


        return {
            "success":
                True,

            "status":
                "BACKUP_VERIFIED",

            "backup":
                result,
        }


    except ValueError as error:

        return api_error(
            status_code=400,
            status=
                "INVALID_BACKUP_ID",

            message=
                str(
                    error
                ),
        )


    except FileNotFoundError:

        return api_error(
            status_code=404,
            status=
                "BACKUP_NOT_FOUND",

            message=
                "Sauvegarde introuvable.",
        )


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "BACKUP_VERIFY_FAILED",

            message=
                str(
                    error
                ),
        )


# ============================================================
# PREPARE RESTORE REQUEST
#
# Cette route :
# 1. prépare/valide la restauration
# 2. crée PRE_RESTORE
# 3. crée restore_pending.json
#
# Elle NE lance PAS l'Executor LIVE.
# ============================================================

@router.post(
    "/api/backups/{backup_id}/restore/prepare"
)
async def prepare_restore(
    backup_id: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.restore",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    try:

        backup_id = (
            validated_backup_id(
                backup_id
            )
        )

    except ValueError as error:

        return api_error(
            status_code=400,
            status=
                "INVALID_BACKUP_ID",

            message=
                str(
                    error
                ),
        )


    actor = session_actor(
        session
    )

    store = (
        live_restore_processor
        .request_store
    )


    try:

        with backup_mutation_lock:

            # -----------------------------------------------
            # ONE RESTORE AT A TIME
            # -----------------------------------------------

            if store.has_in_progress():

                return api_error(
                    status_code=409,
                    status=
                        "RESTORE_IN_PROGRESS",

                    message=
                        "Une restauration est déjà "
                        "marquée IN_PROGRESS.",
                )


            if store.has_pending():

                return api_error(
                    status_code=409,
                    status=
                        "RESTORE_ALREADY_PENDING",

                    message=
                        "Une demande de restauration "
                        "est déjà en attente.",
                )


            # -----------------------------------------------
            # EXISTENCE / INTEGRITY
            # -----------------------------------------------

            backup_catalog.get_backup(
                backup_id,
                verify_files=True,
            )


            # -----------------------------------------------
            # OFFICIAL RESTORE PREPARATION
            # -----------------------------------------------

            prepared = (
                restore_service
                .prepare_restore(
                    backup_id
                )
            )


            if not isinstance(
                prepared,
                dict,
            ):

                raise RuntimeError(
                    "Résultat de préparation "
                    "Restore invalide."
                )


            if (
                prepared.get(
                    "success"
                )
                is not True
            ):

                return api_response(
                    prepared,
                    status_code=409,
                )


            if (
                prepared.get(
                    "status"
                )
                !=
                "READY_TO_RESTORE"
            ):

                return api_response(
                    prepared,
                    status_code=409,
                )


            pre_restore_backup_id = (
                extract_pre_restore_backup_id(
                    prepared
                )
            )


            # -----------------------------------------------
            # PRE_RESTORE MUST BE VALID
            # -----------------------------------------------

            pre_restore = (
                backup_catalog
                .get_backup(
                    pre_restore_backup_id,
                    verify_files=True,
                )
            )


            if (
                pre_restore.get(
                    "status"
                )
                !=
                "AVAILABLE"
            ):

                raise RuntimeError(
                    "PRE_RESTORE indisponible."
                )


            # -----------------------------------------------
            # DURABLE PENDING REQUEST
            # -----------------------------------------------

            restore_request = (
                store.create_pending(
                    backup_id=
                        backup_id,

                    pre_restore_backup_id=
                        pre_restore_backup_id,

                    actor=
                        actor,
                )
            )


        return api_response(
            {
                "success":
                    True,

                "status":
                    "RESTORE_REQUESTED",

                "backup_id":
                    backup_id,

                "pre_restore_backup_id":
                    pre_restore_backup_id,

                "live_restore_enabled":
                    LIVE_RESTORE_ENABLED,

                "preparation":
                    prepared,

                "request":
                    restore_request,

                "message":
                    (
                        "Restauration préparée. "
                        "L'écriture LIVE n'est pas "
                        "déclenchée par cette API."
                    ),
            },
            status_code=202,
        )


    except FileNotFoundError:

        return api_error(
            status_code=404,
            status=
                "BACKUP_NOT_FOUND",

            message=
                "Sauvegarde introuvable.",
        )


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "RESTORE_PREPARE_FAILED",

            message=
                str(
                    error
                ),
        )


# ============================================================
# MIGRATE BACKUP
# ============================================================

@router.post(
    "/api/backups/{backup_id}/migrate"
)
async def migrate_backup(
    backup_id: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.migrate",
    ):

        return forbidden()


    if not request_origin_allowed(
        request
    ):

        return origin_forbidden()


    try:

        backup_id = (
            validated_backup_id(
                backup_id
            )
        )

    except ValueError as error:

        return api_error(
            status_code=400,
            status=
                "INVALID_BACKUP_ID",

            message=
                str(
                    error
                ),
        )


    actor = session_actor(
        session
    )


    try:

        with backup_mutation_lock:

            result = (
                backup_migration_service
                .migrate_and_publish(
                    backup_id,
                    actor=
                        actor,
                )
            )


        if result.get(
            "success"
        ):

            return api_response(
                result,
                status_code=200,
            )


        return api_response(
            result,
            status_code=409,
        )


    except FileNotFoundError:

        return api_error(
            status_code=404,
            status=
                "BACKUP_NOT_FOUND",

            message=
                "Sauvegarde introuvable.",
        )


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "BACKUP_MIGRATION_FAILED",

            message=
                str(
                    error
                ),
        )


# ============================================================
# BACKUP DETAILS
#
# Garder après /restore/status.
# ============================================================

@router.get(
    "/api/backups/{backup_id}"
)
async def backup_details(
    backup_id: str,
    request: Request,
):

    session = get_valid_session(
        request
    )


    if session is None:

        return unauthorized()


    if not session_has_permission(
        session,
        "backups.view",
    ):

        return forbidden()


    try:

        backup_id = (
            validated_backup_id(
                backup_id
            )
        )


        result = (
            backup_catalog
            .get_backup(
                backup_id,
                verify_files=False,
            )
        )


        return {
            "success":
                True,

            "backup":
                result,
        }


    except ValueError as error:

        return api_error(
            status_code=400,
            status=
                "INVALID_BACKUP_ID",

            message=
                str(
                    error
                ),
        )


    except FileNotFoundError:

        return api_error(
            status_code=404,
            status=
                "BACKUP_NOT_FOUND",

            message=
                "Sauvegarde introuvable.",
        )


    except Exception as error:

        return api_error(
            status_code=500,
            status=
                "BACKUP_DETAILS_FAILED",

            message=
                str(
                    error
                ),
        )
