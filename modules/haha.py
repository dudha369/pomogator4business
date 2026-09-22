import asyncio

from core.context import CommandContext
from core.registry import command

_PHRASES = ["ХАХАХАХАХА", "🤣🤣🤣", "ой не могу", "просто умора", "😂😂😂"]


@command(name="haha", module="haha", description="Отправляет пять сообщений со смехом")
async def cmd_haha(ctx: CommandContext):
    await ctx.delete_command_message()
    for phrase in _PHRASES:
        await ctx.answer(phrase)
        await asyncio.sleep(0.4)
