import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))

def sanitize_query(text: str) -> str:
    return text.strip()[:200]

def is_valid_username(username: str) -> bool:
    return 2 <= len(username.strip()) <= 64
