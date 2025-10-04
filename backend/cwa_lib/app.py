from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from common import FRONTEND_DIR_STATIC, CORS_ORIGINS

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
