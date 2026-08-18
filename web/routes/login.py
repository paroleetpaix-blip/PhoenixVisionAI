from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login():

    with open(

        "web/templates/login.html",

        "r",

        encoding="utf-8"

    ) as file:

        return file.read()