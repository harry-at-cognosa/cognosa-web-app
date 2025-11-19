import os
from common.sql_db_sync import wait_for_database
wait_for_database()

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse

from cwa_lib.app import app, templates
from cwa_lib.routers import api_router

app.include_router(api_router)  # must be here, after all other API routes, and before page routes


@app.get("/", tags=["Index page"], include_in_schema=False)
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
