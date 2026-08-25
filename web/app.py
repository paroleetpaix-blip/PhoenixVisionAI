from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from web.routes.dashboard import router

from web.routes.api import router as api_router

from web.routes.video import router as video_router

from web.routes.camera import router as camera_router


from web.routes.events import router as events_router

from web.routes.alerts import router as alerts_router

from web.routes.history import router as history_router

from web.routes.map import router as map_router

from web.routes.anpr import router as anpr_router
from web.routes.reports import router as reports_router
from web.routes.settings import router as settings_router
from web.routes.enterprise import router as enterprise_router

from web.routes.current_vehicle import router as current_vehicle_router

from web.routes.launcher import router as launcher_router

from web.routes.login import router as login_router

from web.routes.auth import router as auth_router

from web.routes.admin_requests import (
    router as admin_requests_router
)

from web.routes.account_request import (
    router as account_request_router
)

from web.routes.change_password import (
    router as change_password_router
)

from web.routes.logout import router as logout_router

from web.routes.users import router as users_router

app = FastAPI(
    title="Phoenix Vision AI"
)

app.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="static"
)

app.include_router(launcher_router)

app.include_router(login_router)

app.include_router(router)

app.include_router(api_router)

app.include_router(video_router)

app.include_router(enterprise_router)

app.include_router(camera_router)


app.include_router(events_router)

app.include_router(alerts_router)

app.include_router(history_router)

app.include_router(map_router)

app.include_router(anpr_router)
app.include_router(reports_router)
app.include_router(settings_router)
app.include_router(current_vehicle_router)

app.include_router(auth_router)

app.include_router(logout_router)

app.include_router(
    account_request_router
)

app.include_router(
    admin_requests_router
)

app.include_router(
    change_password_router
)

app.include_router(users_router)
