import random

from core.context import CommandContext
from core.i18n import t
from core.registry import command

_ANSWER_COUNT = 12


@command(name="8ball", module="eightball", description="Магический шар")
async def cmd_8ball(ctx: CommandContext):
    args = ctx.args.strip()

    if not args:
        await ctx.reply(ctx.t("eightball.usage"))
        return

    index = random.randint(1, _ANSWER_COUNT)
    await ctx.edit_command_message(
        f"""
    <quote>{args}</quote>
    ────────────────────
    🎱 Шар говорит: <b>{ctx.t(f'eightball.answer_{index}')}</b>
    ────────────────────""",
        parse_mode="html",
    )
