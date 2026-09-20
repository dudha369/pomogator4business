import asyncio
import random

from core.context import CommandContext
from core.registry import command

_FRAMES = ["🪙", "🌀", "🪙", "🌀"]


@command(name="flip", module="flip", description="Подбрасывает монетку")
async def cmd_flip(ctx: CommandContext):
    await ctx.delete_command_message()

    sent = await ctx.reply(_FRAMES[0])

    for frame in _FRAMES[1:]:
        await asyncio.sleep(0.35)
        try:
            await ctx.bot.edit_message_text(
                business_connection_id=ctx.connection_id,
                chat_id=ctx.chat_id,
                message_id=sent.message_id,
                text=frame,
            )
        except Exception:
            pass

    result = random.choice(["Орёл", "Решка"])
    await asyncio.sleep(0.35)

    try:
        await ctx.bot.edit_message_text(
            business_connection_id=ctx.connection_id,
            chat_id=ctx.chat_id,
            message_id=sent.message_id,
            text=f"🪙 {result}!",
        )
    except Exception:
        pass
