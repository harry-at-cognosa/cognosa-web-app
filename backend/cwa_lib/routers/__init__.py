from fastapi import APIRouter

from common import API_URL_PREFIX

from cwa_lib.pydantic_schemas.user import UserRead, UserCreate
from cwa_lib.users import fastapi_users, auth_backend
from cwa_lib.routers.users import router__users
from cwa_lib.routers.doc_tasks import router__doc_tasks
from cwa_lib.routers.manage_contexts import router__manage_contexts
from cwa_lib.routers.ga_manage_doc_tasks import router__ga_manage_doc_tasks
from cwa_lib.routers.ga_manage_users import router__ga_manage_users
from cwa_lib.routers.ga_manage_vdbs import router__ga_manage_vdbs
from cwa_lib.routers.ga_settings import router__ga_settings
from cwa_lib.routers.su_change_oneself import router__su_change_oneself
from cwa_lib.routers.su_manage_api_settings import router__su_manage_api_settings
from cwa_lib.routers.su_manage_doc_tasks import router__su_manage_doc_tasks
from cwa_lib.routers.su_manage_users import router__su_manage_users
from cwa_lib.routers.su_manage_groups import router__su_manage_groups
from cwa_lib.routers.su_manage_log_crud import router__su_manage_log_crud
from cwa_lib.routers.su_manage_llms import router__su_manage_llms
from cwa_lib.routers.su_manage_vdbs import router__su_manage_vdbs
from cwa_lib.routers.su_server_status import router__su_server_status
from cwa_lib.routers.misc import router__misc
from cwa_lib.routers.webapp_options import router__webapp_options

api_router = APIRouter(prefix=API_URL_PREFIX)

# Auth & user routes from fastapi-users
api_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"])
api_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["Auth"])
api_router.include_router(router__users, tags=["Users"])

api_router.include_router(router__doc_tasks)
api_router.include_router(router__manage_contexts, tags=["Manage Contexts"])
api_router.include_router(router__misc)
api_router.include_router(router__webapp_options)

api_router.include_router(router__ga_manage_users, tags=["Manage Users (For group admins only)"])
api_router.include_router(router__ga_manage_doc_tasks, tags=["Manage Doc Tasks (For group admins only)"])
api_router.include_router(router__ga_manage_vdbs, tags=["Manage Collections (For group admins only)"])
api_router.include_router(router__ga_settings, tags=["Manage Group Settings (For group admins only)"])

api_router.include_router(router__su_manage_groups, tags=["Superuser Manage Groups"], include_in_schema=False)
api_router.include_router(router__su_manage_vdbs, tags=["Superuser Manage VDBs"], include_in_schema=False)
api_router.include_router(router__su_manage_llms, tags=["Superuser Manage LLMs"], include_in_schema=False)
api_router.include_router(router__su_server_status, tags=["Superuser Server Status"], include_in_schema=False)
api_router.include_router(router__su_manage_users, tags=["Superuser Manage Users"], include_in_schema=False)
api_router.include_router(router__su_manage_api_settings, tags=["Superuser Manage Api Settings"], include_in_schema=False)
api_router.include_router(router__su_manage_doc_tasks, tags=["Superuser Manage Doc Tasks"], include_in_schema=False)
api_router.include_router(router__su_manage_log_crud, tags=["Superuser Manage Log CRUD"], include_in_schema=False)
api_router.include_router(router__su_change_oneself, tags=["Superuser Change Oneself"], include_in_schema=False)
