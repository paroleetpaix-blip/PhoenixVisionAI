from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard():

    with open(
        "web/templates/dashboard.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()