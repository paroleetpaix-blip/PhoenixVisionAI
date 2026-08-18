"""
========================================================
PHOENIX VISION AI

Authentication Routes

Phoenix Security Technologies
========================================================
"""

from fastapi import (
    APIRouter,
    Form,
    Request
)

from fastapi.responses import (
    JSONResponse
)

from core.security.auth import (
    authenticate
)

from core.security.session import (
    session_manager
)

import json

from pathlib import Path

router = APIRouter()

APPROVED_USERS_FILE = Path(
    "data/approved_users.json"
)


def find_approved_user(
    username
):

    if not username:

        return None


    if not APPROVED_USERS_FILE.exists():

        return None


    try:

        with open(
            APPROVED_USERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError
    ):

        return None


    users = []


    if isinstance(
        data,
        list
    ):

        users = data


    elif isinstance(
        data,
        dict
    ):

        for key in (
            "users",
            "approved_users",
            "accounts"
        ):

            value = data.get(
                key
            )


            if isinstance(
                value,
                list
            ):

                users = value

                break


        if not users:

            for key, value in data.items():

                if not isinstance(
                    value,
                    dict
                ):

                    continue


                user = dict(
                    value
                )


                user.setdefault(
                    "username",
                    key
                )


                users.append(
                    user
                )


    target = str(
        username
    ).strip().lower()


    for user in users:

        if not isinstance(
            user,
            dict
        ):

            continue


        account_username = (

            user.get(
                "username"
            )

            or

            user.get(
                "assigned_username"
            )

        )


        if not account_username:

            continue


        if (
            str(account_username)
            .strip()
            .lower()
            ==
            target
        ):

            return user


    return None


def get_photo_url(
    photo
):

    if not photo:

        return None


    value = str(
        photo
    ).replace(
        "\\",
        "/"
    ).strip()


    if value.startswith(
        "/static/"
    ):

        return value


    if value.startswith(
        "static/"
    ):

        return "/" + value


    if value.startswith(
        "web/static/"
    ):

        return (
            "/"
            +
            value[
                len("web/"):
            ]
        )


    if "/" not in value:

        return (
            "/static/uploads/users/"
            +
            value
        )


    return None


# ========================================================
# LOGIN
# ========================================================

@router.post(
    "/api/login"
)
def login(

    username: str = Form(...),

    password: str = Form(...)

):

    user = authenticate(

        username,

        password

    )


    if user is None:

        return JSONResponse(

            status_code=401,

            content={

                "success": False,

                "message":
                    "Identifiants incorrects"

            }

        )


    response = JSONResponse(

        content={

            "success":
                True,

            "username":
                user["username"],

            "role":
                user["role"],

            "token":
                user["token"],

            "must_change_password":
                user.get(
                    "must_change_password",
                    False
                )

        }

    )


    response.set_cookie(

        key="phoenix_token",

        value=user["token"],

        httponly=True,

        samesite="strict",

        secure=False

    )


    return response


# ========================================================
# CURRENT AUTHENTICATED USER
# ========================================================

@router.get(
    "/api/session/me"
)
def session_me(
    request: Request
):

    token = request.cookies.get(
        "phoenix_token"
    )


    if token is None:

        return JSONResponse(

            status_code=401,

            content={

                "success":
                    False,

                "message":
                    "Aucune session active."

            }

        )


    session = session_manager.get(
        token
    )


    if session is None:

        return JSONResponse(

            status_code=401,

            content={

                "success":
                    False,

                "message":
                    "Session invalide ou expirée."

            }

        )


    username = session.get(
        "username"
    )


    role = session.get(
        "role"
    )


    profile = find_approved_user(
        username
    )


    photo_url = None

    display_name = username


    if profile:

        photo_url = get_photo_url(
            profile.get(
                "photo"
            )
        )


        first_name = str(
            profile.get(
                "prenom"
            )
            or
            ""
        ).strip()


        last_name = str(
            profile.get(
                "nom"
            )
            or
            ""
        ).strip()


        complete_name = (
            f"{first_name} {last_name}"
            .strip()
        )


        if complete_name:

            display_name = (
                complete_name
            )


    return {

        "success":
            True,

        "username":
            username,

        "display_name":
            display_name,

        "role":
            role,

        "photo_url":
            photo_url

    }