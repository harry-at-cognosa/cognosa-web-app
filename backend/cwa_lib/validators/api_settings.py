from common.enums.api_settings_names import API_SETTINGS_NAMES_LIST
from sqlalchemy import select
from fastapi.exceptions import RequestValidationError
from common.sql_db_async import AsyncSession
from common.sql_models import ApiSettings


def validate__name(name: str) -> str:
    if name not in API_SETTINGS_NAMES_LIST:
        raise ValueError("Wrong name")
    return name


async def check_unique__name(session: AsyncSession, name: str):
    # check if this name exists in `api_settings` table
    result = await session.execute(select(ApiSettings).where(ApiSettings.name==name))
    exists = result.scalar_one_or_none()
    if exists:
        raise RequestValidationError([
            {
                "loc": ("body", "name"),  # Location: body.name field
                "msg": f"Option '{name}' is already created. Use Edit.",
                "type": "value_error",
                "input": name,
            }
        ])