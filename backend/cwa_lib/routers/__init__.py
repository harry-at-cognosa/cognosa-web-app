from fastapi import APIRouter

from common import API_URL_PREFIX

from cwa_lib.pydantic_schemas.user import UserRead, UserCreate, UserUpdate
from cwa_lib.users import fastapi_users, auth_backend
from cwa_lib.routers.doc_tasks import router__doc_tasks
from cwa_lib.routers.group_contexts import router__group_contexts
from cwa_lib.routers.group_vdbs import router__group_vdbs
from cwa_lib.routers.group_llms import router__group_llms
from cwa_lib.routers.manage_contexts import router__manage_contexts
from cwa_lib.routers.misc import router__misc
from cwa_lib.routers.login_by_username import router__login_by_username

api_router = APIRouter(prefix=API_URL_PREFIX)

# Auth & user routes from fastapi-users
api_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
api_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"])
api_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["Users"])
api_router.include_router(router__login_by_username, tags=["Auth"])

api_router.include_router(router__doc_tasks)
api_router.include_router(router__group_contexts)
api_router.include_router(router__group_vdbs)
api_router.include_router(router__group_llms)
api_router.include_router(router__manage_contexts)
api_router.include_router(router__misc)
