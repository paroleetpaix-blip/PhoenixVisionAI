from fastapi import APIRouter

from fastapi.responses import RedirectResponse

from core.security.session import session_manager

router = APIRouter()


@router.get("/logout")
def logout():

    response = RedirectResponse(

        "/login",

        status_code=302

    )

    response.delete_cookie(

        "phoenix_token"

    )

    return response
