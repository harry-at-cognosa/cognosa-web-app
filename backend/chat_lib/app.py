from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from common import API_URL_PREFIX, CORS_ORIGINS, log
from cwa_lib.middleware.last_seen import refresh_last_seen
from chat_lib.heartbeat import Heartbeat
from chat_lib.routers import router__chat

CHAT_URL_PREFIX = API_URL_PREFIX + '/chat'


@asynccontextmanager
async def lifespan(app: FastAPI):
    heartbeat = Heartbeat()
    await heartbeat.start()
    log.info("Chat service started")
    yield
    await heartbeat.stop()
    log.info("Chat service stopped")


app = FastAPI(
    title="Cognosa Chat API",
    version="1.0",
    lifespan=lifespan,
    dependencies=[Depends(refresh_last_seen)],
)

# The browser reaches this service on its own port when there is no reverse
# proxy in front (local runs), so it needs the same CORS allowance as the web app.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router__chat, prefix=CHAT_URL_PREFIX, tags=["Chat"])
