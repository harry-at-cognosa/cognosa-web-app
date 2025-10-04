import os
import uuid
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication import JWTStrategy

from common import API_URL_PREFIX
from common.sql_db_async import async_get_user_db
from common.sql_models import User

SECRET = os.getenv("SECRET", "INSECURE_CHANGE_ME")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_manager(user_db=Depends(async_get_user_db)) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)

# OAuth2 Bearer transport (Authorization: Bearer <token>) at this token URL
bearer_transport = BearerTransport(tokenUrl=f"{API_URL_PREFIX}/auth/jwt/login".lstrip('/'))  # relative to router prefix

def get_jwt_strategy() -> JWTStrategy:
    # 7 days
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 60 * 24 * 7)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])
