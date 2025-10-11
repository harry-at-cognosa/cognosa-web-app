from contextlib import asynccontextmanager
import os
from traceback import format_exc

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from common import FRONTEND_DIR_STATIC, CORS_ORIGINS, log

from cwa_lib.users import fastapi_users
from fastapi_users.password import PasswordHelper


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass  # init before start up
    yield
    # Clean up after web app stop
    pass

app = FastAPI(title="Cognosa Tasks API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=FRONTEND_DIR_STATIC), name="static")
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR_STATIC, "assets")), name="assets")
templates = Jinja2Templates(directory=FRONTEND_DIR_STATIC)

# A tiny protected endpoint (alt to /users/me)
current_active_user = fastapi_users.current_user(active=True)
password_helper = PasswordHelper()


def get_client_ip(request: Request) -> str:
    """
    Get client's ip. Behind proxy if specified.
    """
    try:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    except Exception:
        log.error(f"Error in get_client_ip:\n{format_exc()}")
    return "unknown"
