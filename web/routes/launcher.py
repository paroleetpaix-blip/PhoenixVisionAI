from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def launcher():

    with open(

        "web/templates/launcher.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()