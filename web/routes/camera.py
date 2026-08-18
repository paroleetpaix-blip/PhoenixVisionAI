from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/camera/{camera_name}", response_class=HTMLResponse)
async def camera_view(camera_name: str):

    with open(
        "web/templates/camera_view.html",
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    return html.replace(
        "{{CAMERA_NAME}}",
        camera_name
    )