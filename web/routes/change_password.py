"""
========================================================
PHOENIX VISION AI

First Login Password Change

Phoenix Security Technologies
========================================================
"""

from datetime import datetime

from pathlib import Path

import hashlib
import hmac
import json
import os
import re
import secrets


from fastapi import (
    APIRouter,
    Form,
    Request
)


from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse
)


from core.security.session import (
    session_manager
)


router = APIRouter()


APPROVED_USERS_FILE = Path(
    "data/approved_users.json"
)


PASSWORD_MIN_LENGTH = 12


# ========================================================
# USERS
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


    temporary_file = (
        APPROVED_USERS_FILE
        .with_suffix(
            ".tmp"
        )
    )


    with temporary_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            users,

            file,

            ensure_ascii=False,

            indent=4

        )


    os.replace(

        temporary_file,

        APPROVED_USERS_FILE

    )


# ========================================================
# PASSWORD SECURITY
# ========================================================


def verify_password(
    password,
    user
):

    try:

        salt = bytes.fromhex(
            user[
                "password_salt"
            ]
        )


        expected_hash = bytes.fromhex(
            user[
                "password_hash"
            ]
        )


    except (
        KeyError,
        ValueError
    ):

        return False


    calculated_hash = (
        hashlib.pbkdf2_hmac(

            "sha256",

            password.encode(
                "utf-8"
            ),

            salt,

            210_000

        )
    )


    return hmac.compare_digest(

        calculated_hash,

        expected_hash

    )


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


def password_is_strong(
    password
):

    if len(password) < PASSWORD_MIN_LENGTH:

        return False


    if not re.search(
        r"[A-Z]",
        password
    ):

        return False


    if not re.search(
        r"[a-z]",
        password
    ):

        return False


    if not re.search(
        r"[0-9]",
        password
    ):

        return False


    if not re.search(
        r"[^A-Za-z0-9]",
        password
    ):

        return False


    return True


# ========================================================
# CURRENT SESSION
# ========================================================


def get_session(
    request: Request
):

    token = request.cookies.get(
        "phoenix_token"
    )


    if token is None:

        return (
            None,
            None
        )


    session = session_manager.get(
        token
    )


    if session is None:

        return (
            token,
            None
        )


    return (
        token,
        session
    )


# ========================================================
# PAGE
# ========================================================


@router.get(
    "/change-password",
    response_class=HTMLResponse
)
async def change_password_page(
    request: Request
):

    token, session = get_session(
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


    users = load_approved_users()


    user = next(

        (

            account

            for account in users

            if account.get(
                "username"
            )
            ==
            username

        ),

        None

    )


    #Cette route concerne uniquement
    #les comptes approuvés.

    if user is None:

        return RedirectResponse(

            "/enterprise",

            status_code=302

        )


    if not user.get(
        "must_change_password",
        False
    ):

        return RedirectResponse(

            "/enterprise",

            status_code=302

        )


    with open(

        "web/templates/change_password.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()


# ========================================================
# CHANGE PASSWORD API
# ========================================================


@router.post(
    "/api/change-password"
)
async def change_password(

    request: Request,

    current_password: str = Form(...),

    new_password: str = Form(...),

    confirm_password: str = Form(...)

):

    token, session = get_session(
        request
    )


    if session is None:

        return JSONResponse(

            status_code=401,

            content={

                "success": False,

                "message":
                    "Votre session a expiré."

            }

        )


    username = session.get(
        "username"
    )


    users = load_approved_users()


    user = next(

        (

            account

            for account in users

            if account.get(
                "username"
            )
            ==
            username

        ),

        None

    )


    if user is None:

        return JSONResponse(

            status_code=404,

            content={

                "success": False,

                "message":
                    "Compte utilisateur introuvable."

            }

        )


    if not user.get(
        "must_change_password",
        False
    ):

        return JSONResponse(

            status_code=409,

            content={

                "success": False,

                "message":
                    "Le changement obligatoire du mot de passe a déjà été effectué."

            }

        )


    if not verify_password(

        current_password,

        user

    ):

        return JSONResponse(

            status_code=401,

            content={

                "success": False,

                "message":
                    "Le mot de passe temporaire est incorrect."

            }

        )


    if (
        new_password
        !=
        confirm_password
    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Les nouveaux mots de passe ne correspondent pas."

            }

        )


    if (
        new_password
        ==
        current_password
    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Le nouveau mot de passe doit être différent du mot de passe temporaire."

            }

        )


    if not password_is_strong(
        new_password
    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Le nouveau mot de passe ne respecte pas les exigences de sécurité."

            }

        )


    if (

        username

        and

        username.lower()
        in
        new_password.lower()

    ):

        return JSONResponse(

            status_code=400,

            content={

                "success": False,

                "message":
                    "Le mot de passe ne doit pas contenir votre identifiant Phoenix."

            }

        )


    new_password_data = (
        hash_password(
            new_password
        )
    )


    user[
        "password_salt"
    ] = new_password_data[
        "salt"
    ]


    user[
        "password_hash"
    ] = new_password_data[
        "hash"
    ]


    user[
        "must_change_password"
    ] = False


    user[
        "password_changed_at"
    ] = (
        datetime.now()
        .isoformat(
            timespec="seconds"
        )
    )


    save_approved_users(
        users
    )


    # ====================================================
    # Rotation de session
    # ====================================================

    role = session.get(
        "role",
        user.get(
            "role",
            "OPERATOR"
        )
    )


    session_manager.remove(
        token
    )


    new_token = (
        session_manager.create(

            username,

            role

        )
    )


    response = JSONResponse(

        content={

            "success": True,

            "message":
                "Mot de passe modifié avec succès."

        }

    )


    response.set_cookie(

        key="phoenix_token",

        value=new_token,

        httponly=True,

        samesite="strict",

        secure=False

    )


    return response