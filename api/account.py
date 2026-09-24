"""Сводка для вкладки "Аккаунт" мини-приложения: подключение, зеркало,
эмодзи-статус."""

import json

from fastapi import APIRouter, Depends

from api.deps import require_user
from core import database as db

router = APIRouter()


@router.get("/account")
async def get_account(user: dict = Depends(require_user)):
    owner_id = user["id"]
    connection = await db.get_connection_by_owner(owner_id)

    connection_info = None
    if connection:
        try:
            rights = (
                json.loads(connection["rights_json"])
                if connection.get("rights_json")
                else {}
            )
        except (json.JSONDecodeError, TypeError):
            rights = {}

        connection_info = {
            "owner_name": connection.get("owner_name"),
            "owner_username": connection.get("owner_username"),
            "prefix": connection["prefix"],
            "rights": rights,
        }

    mirror = await db.get_mirror(owner_id)
    mirror_info = {
        "connected": bool(mirror and mirror["is_active"]),
        "username": mirror["bot_username"] if mirror else None,
    }

    return {
        "connection": connection_info,
        "mirror": mirror_info,
        "emoji_status": {
            "granted": await db.is_emoji_status_granted(owner_id),
            "enabled": await db.is_emoji_status_enabled(owner_id),
        },
    }
