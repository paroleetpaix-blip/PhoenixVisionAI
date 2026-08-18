from fastapi import APIRouter

from fastapi.responses import StreamingResponse

from core import runtime

import time


router = APIRouter()


def stream(camera_id):

    while True:

        engine = runtime.engine

        if engine is None:

            time.sleep(0.05)

            continue

        jpeg = engine.frame_hub.latest_jpeg(

            camera_id

        )

        if jpeg is None:

            time.sleep(0.01)

            continue

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + jpeg +

            b"\r\n"

        )


@router.get("/video/{camera_id}")

def video(camera_id):

    return StreamingResponse(

        stream(camera_id),

        media_type="multipart/x-mixed-replace; boundary=frame"

    )