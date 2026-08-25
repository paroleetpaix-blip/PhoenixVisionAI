"""
========================================================
PHOENIX VISION AI

Phoenix Admin
Account Request Validation

Phoenix Security Technologies
========================================================
"""

from datetime import datetime

from pathlib import Path

import hashlib
import json
import re
import secrets


from fastapi import (
    APIRouter,
    File,
    Form,
    Request,
    UploadFile
)


from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse
)


from core.security.permissions import (
    session_has_permission,
)


from core.security.session import (
    session_manager
)

from core.email.email_service import (
    email_service
)

from web.routes.account_request import (
    load_requests,
    save_requests
)


from core.users_registry.user_service import (
    user_registry_service,
)

router = APIRouter()


APPROVED_USERS_FILE = Path(
    "data/approved_users.json"
)


UPLOAD_DIRECTORY = Path(
    "web/static/uploads/users"
)


USERNAME_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*\d)[a-z0-9]{5,20}$"
)


ALLOWED_ROLES = {

    "OPERATOR",
    "SUPERVISOR",
    "ANALYST"

}


ALLOWED_ACCESS_LEVELS = {

    "STANDARD",
    "SENSITIVE",
    "RESTRICTED"

}


# ========================================================
# ADMIN SESSION
# ========================================================

def get_admin_session(
    request: Request
):

    token = request.cookies.get(
        "phoenix_token"
    )


    if token is None:

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


    if not session_has_permission(
        session,
        "users.approve_request",
    ):

        return None


    return session


# ========================================================
# USERS DATABASE
# ========================================================

def load_approved_users():

    if not APPROVED_USERS_FILE.exists():

        return []


    try:

        with APPROVED_USERS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


def save_approved_users(
    users
):

    APPROVED_USERS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with APPROVED_USERS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            users,

            file,

            ensure_ascii=False,

            indent=4

        )


# ========================================================
# PASSWORD
# ========================================================

def create_temporary_password():

    alphabet = (

        "ABCDEFGHJKLMNPQRSTUVWXYZ"
        "abcdefghijkmnopqrstuvwxyz"
        "23456789"
        "!@#"
    )


    while True:

        password = "".join(

            secrets.choice(
                alphabet
            )

            for _ in range(12)

        )


        if (

            any(
                character.isupper()
                for character in password
            )

            and

            any(
                character.islower()
                for character in password
            )

            and

            any(
                character.isdigit()
                for character in password
            )

        ):

            return password


def hash_password(
    password
):

    salt = secrets.token_bytes(
        16
    )


    digest = hashlib.pbkdf2_hmac(

        "sha256",

        password.encode(
            "utf-8"
        ),

        salt,

        210_000

    )


    return {

        "salt":
            salt.hex(),

        "hash":
            digest.hex()

    }


# ========================================================
# ADMIN PAGE
# ========================================================

@router.get(
    "/admin/requests",
    response_class=HTMLResponse
)
async def admin_requests_page(
    request: Request
):

    admin_session = get_admin_session(
        request
    )


    if admin_session is None:

        return RedirectResponse(
            "/login",
            status_code=302
        )


    with open(

        "web/templates/admin_requests.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()


# ========================================================
# REQUEST LIST
# ========================================================

@router.get(
    "/api/admin/account-requests"
)
async def admin_account_requests(
    request: Request
):

    admin_session = get_admin_session(
        request
    )


    if admin_session is None:

        return JSONResponse(

            status_code=403,

            content={

                "success": False,

                "message":
                    "Accès administrateur requis."

            }

        )


    requests = load_requests()


    requests.sort(

        key=lambda item:
            item.get(
                "created_at",
                ""
            ),

        reverse=True

    )


    return requests


# ========================================================
# APPROVE / UPDATE REQUEST
# ========================================================

@router.post(
    "/api/admin/account-requests/{request_id}"
)
async def approve_account_request(

    request_id: str,

    request: Request,

    assigned_username: str = Form(...),

    role: str = Form(...),

    access_level: str = Form(...),

    account_expiry: str = Form(""),

    nom: str = Form(...),

    postnom: str = Form(...),

    prenom: str = Form(...),

    sexe: str = Form(...),

    date_naissance: str = Form(...),

    email: str = Form(...),

    telephone: str = Form(...),

    organisation: str = Form(""),

    matricule: str = Form(""),

    departement: str = Form(""),

    fonction: str = Form(""),

    site_affectation: str = Form(""),

    responsable: str = Form(""),

    motif: str = Form(""),

    photo: UploadFile | None = File(
        default=None
    )

):

    admin_session = get_admin_session(
        request
    )


    if admin_session is None:

        return JSONResponse(

            status_code=403,

            content={

                "success": False,

                "message":
                    "Accès administrateur requis."

            }

        )


    username = (
        assigned_username
        .strip()
        .lower()
    )


    role = (
        role
        .strip()
        .upper()
    )


    access_level = (
        access_level
        .strip()
        .upper()
    )


    if not USERNAME_PATTERN.match(
        username
    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Identifiant Phoenix invalide."

            }

        )


    if role not in ALLOWED_ROLES:

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Rôle utilisateur invalide."

            }

        )


    if (
        access_level
        not in
        ALLOWED_ACCESS_LEVELS
    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Niveau d'accès invalide."

            }

        )


    requests = load_requests()


    target = None


    for account_request in requests:

        if (

            account_request.get(
                "request_id"
            )
            ==
            request_id

        ):

            target = account_request

            break


    if target is None:

        return JSONResponse(

            status_code=404,

            content={

                "success": False,

                "message":
                    "Demande introuvable."

            }

        )


    approved_users = (
        load_approved_users()
    )


    existing_account = None


    for user in approved_users:

        if (

            user.get(
                "request_id"
            )
            ==
            request_id

        ):

            existing_account = user


        elif (

            user.get(
                "username"
            )
            ==
            username

        ):

            return JSONResponse(

                status_code=409,

                content={

                    "success": False,

                    "message":
                        "Cet identifiant Phoenix est déjà utilisé."

                }

            )


    # ====================================================
    # PHOTO
    # ====================================================

    photo_url = target.get(
        "photo"
    )


    if (

        photo is not None

        and

        photo.filename

    ):

        allowed_types = {

            "image/jpeg":
                ".jpg",

            "image/png":
                ".png",

            "image/webp":
                ".webp"

        }


        extension = allowed_types.get(
            photo.content_type
        )


        if extension is None:

            return JSONResponse(

                status_code=400,

                content={

                    "success": False,

                    "message":
                        "Format de photo non autorisé."

                }

            )


        content = await photo.read()


        maximum_size = (
            5
            *
            1024
            *
            1024
        )


        if len(content) > maximum_size:

            return JSONResponse(

                status_code=400,

                content={

                    "success": False,

                    "message":
                        "La photo dépasse 5 Mo."

                }

            )


        UPLOAD_DIRECTORY.mkdir(

            parents=True,

            exist_ok=True

        )


        photo_filename = (

            request_id.lower()
            +
            extension

        )


        photo_path = (

            UPLOAD_DIRECTORY
            /
            photo_filename

        )


        photo_path.write_bytes(
            content
        )


        photo_url = (

            "/static/uploads/users/"
            +
            photo_filename

        )


    # ====================================================
    # UPDATE REQUEST
    # ====================================================

    approved_at = (
        target.get(
            "approved_at"
        )
        or
        datetime.now()
        .isoformat(
            timespec="seconds"
        )
    )


    target.update({

        "nom":
            nom.strip(),

        "postnom":
            postnom.strip(),

        "prenom":
            prenom.strip(),

        "sexe":
            sexe.strip(),

        "date_naissance":
            date_naissance.strip(),

        "email":
            email.strip().lower(),

        "telephone":
            telephone.strip(),

        "organisation":
            organisation.strip(),

        "matricule":
            matricule.strip(),

        "departement":
            departement.strip(),

        "fonction":
            fonction.strip(),

        "site_affectation":
            site_affectation.strip(),

        "responsable":
            responsable.strip(),

        "motif":
            motif.strip(),

        "photo":
            photo_url,

        "assigned_username":
            username,

        "role":
            role,

        "access_level":
            access_level,

        "account_expiry":
            account_expiry.strip(),

        "status":
            "APPROVED",

        "approved_at":
            approved_at,

        "approved_by":
            admin_session.get(
                "username"
            )

    })


    temporary_password = None

    account_created = False


    # ====================================================
    # FIRST APPROVAL
    # ====================================================

    if existing_account is None:

        temporary_password = (
            create_temporary_password()
        )


        password_data = (
            hash_password(
                temporary_password
            )
        )


        existing_account = {

            "request_id":
                request_id,

            "password_salt":
                password_data[
                    "salt"
                ],

            "password_hash":
                password_data[
                    "hash"
                ],

            "must_change_password":
                True,

            "created_at":
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )

        }


        approved_users.append(
            existing_account
        )


        account_created = True


    # ====================================================
    # ACCOUNT INFORMATION
    # ====================================================

    existing_account.update({

        "username":
            username,

        "role":
            role,

        "access_level":
            access_level,

        "account_expiry":
            account_expiry.strip(),

        "nom":
            nom.strip(),

        "postnom":
            postnom.strip(),

        "prenom":
            prenom.strip(),

        "sexe":
            sexe.strip(),

        "date_naissance":
            date_naissance.strip(),

        "email":
            email.strip().lower(),

        "telephone":
            telephone.strip(),

        "organisation":
            organisation.strip(),

        "matricule":
            matricule.strip(),

        "departement":
            departement.strip(),

        "fonction":
            fonction.strip(),

        "site_affectation":
            site_affectation.strip(),

        "responsable":
            responsable.strip(),

        "photo":
            photo_url,

        "active":
            True,

        "approved_at":
            approved_at,

        "approved_by":
            admin_session.get(
                "username"
            )

    })


    save_requests(
        requests
    )


    save_approved_users(
        approved_users
    )

    # ====================================================
    # ENTERPRISE USER REGISTRY
    # ====================================================

    try:

        user_registry_service.sync_approved_account(
            existing_account,
            request=
                target,
            actor_username=
                admin_session.get(
                    "username"
                )
                or
                "SYSTEM",
            actor_role=
                admin_session.get(
                    "role"
                )
                or
                "ADMIN",
            reason=
                "Approbation ou mise à jour du compte",
        )

    except Exception as error:

        print(
            "Phoenix User Registry "
            "approval synchronization warning:",
            type(
                error
            ).__name__,
        )


    # ====================================================
    # EMAIL D'ACTIVATION
    # ====================================================

    email_sent = False

    email_status = (
        "NOT_REQUIRED"
    )


    # L'e-mail n'est envoyé que lors
    # de la création initiale du compte.
    #
    # Une simple modification ultérieure
    # ne crée pas un nouveau mot de passe.

    if (
        account_created
        and
        temporary_password
    ):

        email_result = (
            email_service
            .send_account_activation(

                destination=
                    email.strip().lower(),

                first_name=
                    prenom.strip(),

                username=
                    username,

                temporary_password=
                    temporary_password,

                role=
                    role,

                organisation=
                    organisation.strip()

            )
        )


        email_sent = (
            email_result.get(
                "success",
                False
            )
        )


        email_status = (
            email_result.get(
                "reason"
            )
            or
            "SENT"
        )


        target[
            "activation_email_sent"
        ] = email_sent


        target[
            "activation_email_status"
        ] = email_status


        if email_sent:

            target[
                "activation_email_sent_at"
            ] = (
                datetime.now()
                .isoformat(
                    timespec="seconds"
                )
            )


        existing_account[
            "activation_email_sent"
        ] = email_sent


        existing_account[
            "activation_email_status"
        ] = email_status


        save_requests(
            requests
        )


        save_approved_users(
            approved_users
        )


        return {

        "success":
            True,

        "status":
            "APPROVED",

        "username":
            username,

        "account_created":
            account_created,

        "temporary_password":
            temporary_password,

        "email_sent":
            email_sent,

        "email_status":
            email_status

    }
