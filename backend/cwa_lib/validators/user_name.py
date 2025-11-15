import re
from sqlalchemy import select
from fastapi.exceptions import RequestValidationError
from common.sql_db_async import AsyncSession
from common.sql_models import User
from common.sql_models.api_users import User

USERNAME_REGEX = re.compile(r"^[a-z0-9_-]+$")

def validate_user_name(v: str, min_length: int = 3, max_length: int = 32) -> str:
    v = v.lower().strip()
    if not USERNAME_REGEX.match(v):
        raise ValueError("user_name must contain only lowercase letters, numbers, underscores, or hyphens")
    # check minimum and maximum length after cleaning
    if min_length and (len(v) < min_length):
        raise ValueError(f"user_name must contain at least {min_length} valid characters")
    if max_length and (len(v) > max_length):
        raise ValueError(f"user_name is too long (more than {max_length} characters).")
    return v

async def check_unique__email(session: AsyncSession, email: str):
    # check if user exists with the same email
    result = await session.execute(select(User).where(User.email==email)) # type: ignore
    exists = result.scalar_one_or_none()
    if exists:
        raise RequestValidationError([
            {
                "loc": ("body", "email"),  # Location: body.email field
                "msg": "email is already registered",
                "type": "value_error",
                "input": email,
            }
        ])
    
async def check_unique__user_name(session: AsyncSession, user_name: str):
    # check if user exists with the same user_name
    result = await session.execute(select(User).where(User.user_name==user_name))
    exists = result.scalar_one_or_none()
    if exists:
        raise RequestValidationError([
            {
                "loc": ("body", "user_name"),  # Location: body.user_name field
                "msg": "user_name is already registered",
                "type": "value_error",
                "input": user_name,
            }
        ])