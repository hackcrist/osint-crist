import json
from datetime import datetime

def bold(text: str) -> str:
    return f"<b>{text}</b>"

def code(text: str) -> str:
    return f"<code>{text}</code>"

def pre(text: str) -> str:
    return f"<pre>{text}</pre>"

def link(text: str, url: str) -> str:
    return f'<a href="{url}">{text}</a>'

def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_result(data: dict) -> str:
    parts = []
    for k, v in data.items():
        parts.append(f"{bold(k)}: {code(str(v))}")
    return "\n".join(parts)

def paginate(text: str, max_len: int = 4000) -> list[str]:
    pages = []
    while len(text) > max_len:
        idx = text.rfind("\n", 0, max_len)
        if idx == -1:
            idx = max_len
        pages.append(text[:idx])
        text = text[idx:].strip()
    if text:
        pages.append(text)
    return pages
