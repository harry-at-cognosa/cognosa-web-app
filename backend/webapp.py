import os
from common.sql_db_sync import wait_for_database
wait_for_database()
from cwa_lib.sql_tables.api_settings import ApiSettingsTable
ApiSettingsTable.prepare_default_values_at_start()

from fastapi import HTTPException, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from common.sql_db_async import AsyncSession, async_get_session
from cwa_lib.app import app, templates
from cwa_lib.users import current_active_user_or_none
from cwa_lib.routers import api_router
from cwa_lib.sql_tables.api_settings import ApiSettingsTable
from common.sql_models import User


app.include_router(api_router)  # must be here, after all other API routes, and before page routes

@app.get("/app/assets/{filename:path}" , tags=["App"], include_in_schema=False)
async def app_assets(filename: str):
    file_path = os.path.join("static", 'assets', filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(404)    

@app.get("/app" , tags=["App"], include_in_schema=False)
@app.get("/app/{fullpath:path}" , tags=["App"], include_in_schema=False)
async def app_index(request: Request, user: User | None = Depends(current_active_user_or_none)):
    url_path = request.url.path.lstrip('/')
    if url_path.startswith('assets/') or url_path.endswith('manifest.webmanifest'):
        file_path = os.path.join("static", url_path.replace('app/', '').lstrip('/'))
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        raise HTTPException(404)
    if not user:
        return templates.TemplateResponse(name="app_redirect.html", request=request)
    return templates.TemplateResponse(name="index.html", request=request)    


@app.get("/login", tags=["Login page"], include_in_schema=False)
async def login(request: Request):
    """
    Login page
    """
    return templates.TemplateResponse(name="login.html", request=request)


@app.get("/", tags=["Index page"], include_in_schema=False, response_class=HTMLResponse)
async def index(session: AsyncSession = Depends(async_get_session)):
    """
    Index page
    """
    index_html = await ApiSettingsTable(session).select_one('index_page', default='Empty index page')
    return HTMLResponse(index_html)


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, request: Request):
    url_path = request.url.path.lstrip('/')
    if url_path.startswith("api/"):
        raise HTTPException(404)
    file_path = os.path.join("static", url_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(404)
