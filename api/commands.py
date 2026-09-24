"""GET /commands — список всех команд бота для отображения в мини-приложении."""

from fastapi import APIRouter

from core.i18n import t
from core.registry import registry

router = APIRouter()


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
