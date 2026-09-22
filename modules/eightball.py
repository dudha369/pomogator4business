import random

from core.context import CommandContext
from core.registry import command

_ANSWER_COUNT = 12


@command(name="8ball", module="eightball", description="Магический шар")
async def cmd_8ball(ctx: CommandContext):
    args = ctx.args.strip()

    if not args:
        await ctx.delete_command_message()
        await ctx.bot.send_message(
            chat_id=ctx.connection["owner_chat_id"], text=ctx.t("eightball.usage")
        )
        return

    index = random.randint(1, _ANSWER_COUNT)
    await ctx.edit_command_message(
        f"""
<blockquote>{args}</blockquote>
────────────────────
🎱 Шар говорит: <b>{ctx.t(f'eightball.answer_{index}')}</b>
────────────────────""",
        parse_mode="html",
    )
