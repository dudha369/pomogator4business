import asyncio
import random

from core.context import CommandContext
from core.registry import command


@command(name="flip", module="flip", description="Подбрасывает монетку")
async def cmd_flip(ctx: CommandContext):
    await ctx.edit_command_message(
        '<tg-emoji emoji-id="5920267974043766795">🪙</tg-emoji>',
        parse_mode="HTML",
    )

    await asyncio.sleep(2)

    result = random.choice(["ОРЁЛ", "РЕШКА"])

    try:
        await ctx.edit_command_message(
            text=f"""
            ────────────────────
            **Результат**: Выпал{'а' if result == 'РЕШКА' else ''} __**{result}**__! 
            ────────────────────""",
            parse_mode="markdown",
        )
    except Exception:
        pass
