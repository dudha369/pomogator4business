import asyncio

from core.context import CommandContext
from core.registry import command

_PHRASES = [
    "ХАХАХАХАХА",
    "🤣🤣🤣",
    "ой не могу",
    "просто умора",
    "😂😂😂",
    "ХА-ХА-ХА-ХА-ХА",
    "хахахахаха",
    "лол",
    "это реально смешно",
    "это реально приносит мне удовольствие",
    "я гнию на дне озера уже 5 лет",
    "😹😹😹",
]


@command(name="haha", module="haha", description="Отправляет пять сообщений со смехом")
async def cmd_haha(ctx: CommandContext):
    await ctx.edit_command_message(_PHRASES[0])
    for phrase in _PHRASES[1:]:
        await asyncio.sleep(0.4)
        await ctx.reply(phrase)
