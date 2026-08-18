from pathlib import Path

import json


from fastapi import (
    APIRouter,
    Request
)


from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)


from core.security.session import (
    session_manager
)


router = APIRouter()


APPROVED_USERS_FILE = Path(
    "data/approved_users.json"
)


def user_requires_password_change(
    username
):

    if not APPROVED_USERS_FILE.exists():

        return False


    try:

        with APPROVED_USERS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            users = json.load(
                file
            )


    except (
        json.JSONDecodeError,
        OSError
    ):

        return False


    for user in users:

        if (
            user.get("username")
            ==
            username
        ):

            return user.get(
                "must_change_password",
                False
            )


    return False


@router.get(
    "/enterprise",
    response_class=HTMLResponse
)
async def enterprise(
    request: Request
):

    token = request.cookies.get(
        "phoenix_token"
    )


    if token is None:

        return RedirectResponse(

            "/login",

            status_code=302

        )


    if not session_manager.exists(
        token
    ):

        return RedirectResponse(

            "/login",

            status_code=302

        )


    session = session_manager.get(
        token
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

        "web/templates/dashboard_enterprise.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()