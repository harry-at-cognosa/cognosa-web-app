import os
from common.sql_db_sync import wait_for_database
wait_for_database()

from fastapi import HTTPException, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse
from common.sql_db_async import AsyncSession, async_get_session
from cwa_lib.app import app, templates
from cwa_lib.routers import api_router
from cwa_lib.sql_tables.api_settings import ApiSettingsTable

app.include_router(api_router)  # must be here, after all other API routes, and before page routes


@app.get("/", tags=[" page"], include_in_schema=False, response_class=HTMLResponse)
async def index(session: AsyncSession = Depends(async_get_session)):
    """
    Index page
    """
    result = await ApiSettingsTable(session).select_by_names(['index_page'])
    index_html = result['index_page'] or 'Empty index page'
    return HTMLResponse(index_html)


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, request: Request):
    url_path = request.url.path
    if url_path.startswith("/api/"):
        raise HTTPException(status_code=404, detail="Not found")
    file_path = os.path.join("static", full_path)    
    if os.path.exists(file_path):
        return FileResponse(file_path)
    if url_path.startswith('/login') or url_path.startswith('/app'):
        return templates.TemplateResponse(name="index.html", request=request)
    raise HTTPException(404)
