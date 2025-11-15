import re

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
