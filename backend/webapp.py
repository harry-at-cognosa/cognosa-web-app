import os

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse

from cwa_lib.app import app, templates, api_router
from cwa_lib.routers.doc_tasks import router__doc_tasks
from cwa_lib.routers.group_contexts import router__group_contexts
from cwa_lib.routers.group_vdbs import router__group_vdbs
from cwa_lib.routers.manage_contexts import router__manage_contexts
from cwa_lib.routers.misc import router__misc

api_router.include_router(router__doc_tasks)
api_router.include_router(router__group_contexts)
api_router.include_router(router__group_vdbs)
api_router.include_router(router__manage_contexts)
api_router.include_router(router__misc)

app.include_router(api_router)  # must be here, after all other API routes, and before page routes


@app.get("/", tags=["Index page"])
async def index(request: Request):
    """
    Index page
    """
    return templates.TemplateResponse(name="index.html", request=request)


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, request: Request):
    if request.url.path.startswith("/api/"):
        raise HTTPException(status_code=404, detail="Not found")
    file_path = os.path.join("static", full_path)    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return templates.TemplateResponse(name="index.html", request=request)
