import json

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from config import BOT_TOKEN
from core import database as db
from core.i18n import t
from core.registry import registry
from core.telegram_auth import validate_init_data

router = APIRouter()


def require_user(x_telegram_init_data: str = Header(..., alias="X-Telegram-Init-Data")):
    parsed = validate_init_data(x_telegram_init_data, BOT_TOKEN)
    if not parsed:
        raise HTTPException(status_code=401, detail="Invalid init data")

    try:
        user = json.loads(parsed["user"])
    except Exception:
        raise HTTPException(status_code=401, detail="Missing user in init data")

    return user


async def _require_connection(owner_id: int):
    connection = await db.get_connection_by_owner(owner_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Business connection not found")
    return connection


@router.get("/commands")
async def list_commands(locale: str = "ru"):
    result = []
    for module_name, commands in sorted(registry.modules().items()):
        for cmd in commands:
            description = t(f"cmddesc.{cmd.name}", locale)
            if description == f"cmddesc.{cmd.name}":
                description = cmd.description
            result.append(
                {
                    "module": module_name,
                    "name": cmd.name,
                    "aliases": cmd.aliases,
                    "description": description,
                    "owner_only": cmd.owner_only,
                }
            )
    return {"commands": result}


@router.get("/settings")
async def get_settings(user: dict = Depends(require_user)):
    connection = await _require_connection(user["id"])
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

    connection = await _require_connection(user["id"])
    await db.set_prefix(connection["connection_id"], payload.prefix)
    return {"prefix": payload.prefix}


class ModuleToggle(BaseModel):
    module: str
    enabled: bool


@router.post("/settings/module")
async def toggle_module(payload: ModuleToggle, user: dict = Depends(require_user)):
    if payload.module not in registry.modules():
        raise HTTPException(status_code=404, detail="Unknown module")

    connection = await _require_connection(user["id"])
    if payload.enabled:
        await db.enable_module(connection["connection_id"], payload.module)
    else:
        await db.disable_module(connection["connection_id"], payload.module)

    return {"module": payload.module, "enabled": payload.enabled}


@router.get("/emoji-status")
async def get_emoji_status(user: dict = Depends(require_user)):
    return {
        "granted": await db.is_emoji_status_granted(user["id"]),
        "enabled": await db.is_emoji_status_enabled(user["id"]),
    }


@router.get("/locale")
async def get_locale(user: dict = Depends(require_user)):
    return {"locale": await db.get_locale(user["id"])}


class LocaleUpdate(BaseModel):
    locale: str


@router.post("/locale")
async def update_locale(payload: LocaleUpdate, user: dict = Depends(require_user)):
    if payload.locale not in ("ru", "en", "uk"):
        raise HTTPException(status_code=400, detail="Unsupported locale")

    await db.set_locale(user["id"], payload.locale)
    return {"locale": payload.locale}


class EmojiStatusToggle(BaseModel):
    enabled: bool


@router.post("/settings/emoji-status")
async def toggle_emoji_status(
    payload: EmojiStatusToggle, user: dict = Depends(require_user)
):
    if not await db.is_emoji_status_granted(user["id"]):
        raise HTTPException(status_code=400, detail="Access not granted yet")

    await db.set_emoji_status_enabled(user["id"], payload.enabled)
    return {"enabled": payload.enabled}


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
