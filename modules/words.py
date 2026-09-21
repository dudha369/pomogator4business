import asyncio

from core.context import CommandContext
from core.registry import command

_DELAY = 0.5
_MAX_WORDS = 40


@command(name="words", module="words", description="Отправляет фразу по одному слову")
async def cmd_words(ctx: CommandContext):
    if not ctx.args.strip():
        await ctx.reply(ctx.t("words.usage"))
        return

    words = ctx.args.split()[:_MAX_WORDS]
    await ctx.edit_command_message(words.pop(0))

    await asyncio.sleep(_DELAY)

    for word in words:
        await ctx.reply(word)
        await asyncio.sleep(_DELAY)
