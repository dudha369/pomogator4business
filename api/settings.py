"""Настройки подключения: префикс команд, вкл/выкл модулей.

/settings/emoji-status живёт в api/emoji_status.py вместе с остальным про
эмодзи-статус, хоть URL и начинается с /settings."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.deps import require_connection, require_user
from core import database as db
from core.registry import registry

router = APIRouter()


@router.get("/settings")
async def get_settings(user: dict = Depends(require_user)):
    connection = await require_connection(user["id"])
    disabled = await db.list_disabled_modules(connection["connection_id"])

    modules = sorted(registry.modules().keys())
    return {
        "prefix": connection["prefix"],
        "modules": [
            {"name": module_name, "enabled": module_name not in disabled}
            for module_name in modules
        ],
    }


class PrefixUpdate(BaseModel):
    prefix: str


@router.post("/settings/prefix")
async def update_prefix(payload: PrefixUpdate, user: dict = Depends(require_user)):
    if len(payload.prefix) != 1:
        raise HTTPException(
            status_code=400, detail="Prefix must be exactly one character"
        )

    connection = await require_connection(user["id"])
    await db.set_prefix(connection["connection_id"], payload.prefix)
    return {"prefix": payload.prefix}


class ModuleToggle(BaseModel):
    module: str
    enabled: bool


@router.post("/settings/module")
async def toggle_module(payload: ModuleToggle, user: dict = Depends(require_user)):
    if payload.module not in registry.modules():
        raise HTTPException(status_code=404, detail="Unknown module")

    connection = await require_connection(user["id"])
    if payload.enabled:
        await db.enable_module(connection["connection_id"], payload.module)
    else:
        await db.disable_module(connection["connection_id"], payload.module)

    return {"module": payload.module, "enabled": payload.enabled}
