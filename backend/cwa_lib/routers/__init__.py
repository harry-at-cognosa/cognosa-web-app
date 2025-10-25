from fastapi import APIRouter

from common import API_URL_PREFIX

from cwa_lib.pydantic_schemas.user import UserRead, UserCreate
from cwa_lib.users import fastapi_users, auth_backend
from cwa_lib.routers.users import router__users
from cwa_lib.routers.doc_tasks import router__doc_tasks
from cwa_lib.routers.manage_contexts import router__manage_contexts
from cwa_lib.routers.manage_users import router__manage_users
from cwa_lib.routers.manage_groups import router__manage_groups
from cwa_lib.routers.manage_llms import router__manage_llms
from cwa_lib.routers.manage_vdbs import router__manage_vdbs
from cwa_lib.routers.misc import router__misc
from cwa_lib.routers.webapp_options import router__webapp_options
from cwa_lib.routers.login_by_username import router__login_by_username

api_router = APIRouter(prefix=API_URL_PREFIX)

# Auth & user routes from fastapi-users
api_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
api_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"])
api_router.include_router(router__login_by_username, tags=["Auth"])
api_router.include_router(router__users, tags=["Users"])

api_router.include_router(router__doc_tasks)
api_router.include_router(router__manage_contexts, tags=["Manage Contexts"])
api_router.include_router(router__manage_users, include_in_schema=False)
api_router.include_router(router__manage_groups, tags=["Manage Groups"], include_in_schema=False)
api_router.include_router(router__manage_llms, tags=["Manage LLMs"], include_in_schema=False)
api_router.include_router(router__manage_vdbs, tags=["Manage VDBs"], include_in_schema=False)
api_router.include_router(router__misc)
api_router.include_router(router__webapp_options)
