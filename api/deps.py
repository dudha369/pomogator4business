"""Общие зависимости FastAPI-эндпоинтов: проверка initData мини-приложения
и поиск бизнес-подключения по владельцу. Используется всеми файлами api/*.
"""

import json

from fastapi import Header, HTTPException

from config import settings
from core import database as db
from core.telegram_auth import validate_init_data


def require_user(x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")):
    parsed = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)
    if not parsed:
        raise HTTPException(status_code=401, detail="Invalid init data")

    try:
        user = json.loads(parsed["user"])
    except Exception:
        raise HTTPException(status_code=401, detail="Missing user in init data")

    return user


async def require_connection(owner_id: int):
    connection = await db.get_connection_by_owner(owner_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Business connection not found")
    return connection
