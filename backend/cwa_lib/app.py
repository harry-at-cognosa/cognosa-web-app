from contextlib import asynccontextmanager
import os
from traceback import format_exc

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from common import FRONTEND_DIR_STATIC, CORS_ORIGINS, log

from cwa_lib.middleware.last_seen import refresh_last_seen


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass  # init before start up
    yield
    # Clean up after web app stop
    pass

app = FastAPI(
    title="Cognosa Tasks API",
    version="1.0",
    lifespan=lifespan,
    dependencies=[Depends(refresh_last_seen)],
)

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
