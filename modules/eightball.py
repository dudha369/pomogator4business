import random

from core.context import CommandContext
from core.i18n import t
from core.registry import command

_ANSWER_COUNT = 12


@command(name="8ball", module="eightball", description="Магический шар")
async def cmd_8ball(ctx: CommandContext):
    if not ctx.args.strip():
        await ctx.reply(ctx.t("eightball.usage"))
        return

    index = random.randint(1, _ANSWER_COUNT)
    await ctx.delete_command_message()
    await ctx.reply(ctx.t(f"eightball.answer_{index}"))
