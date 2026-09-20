import json

from aiogram import Router
from aiogram.types import BusinessConnection

from core import database as db

router = Router(name="connection")


@router.business_connection()
async def on_business_connection(connection: BusinessConnection):
    rights = connection.rights.model_dump(mode="json") if connection.rights else {}

    await db.upsert_connection(
        connection_id=connection.id,
        owner_id=connection.user.id,
        owner_chat_id=connection.user_chat_id,
        is_enabled=connection.is_enabled,
        owner_name=connection.user.full_name,
        owner_username=connection.user.username,
        rights_json=json.dumps(rights, ensure_ascii=False),
    )
