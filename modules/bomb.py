import asyncio

from core.context import CommandContext
from core.registry import command
from core.utils import parse_duration_loose

_MAX_SECONDS = 24 * 3600


async def _explode(bot, connection_id, message_id, seconds):
    await asyncio.sleep(seconds)
    try:
        await bot.delete_business_messages(
            business_connection_id=connection_id,
            message_ids=[message_id],
        )
    except Exception:
        pass


@command(
    name="bomb",
    aliases=["timerdel"],
    module="bomb",
    description="Отправляет самоудаляющееся сообщение или ставит таймер на удаление ответа",
)
async def cmd_bomb(ctx: CommandContext):
    target = ctx.message.reply_to_message

    if target:
        raw_time = ctx.args.strip().split()[0] if ctx.args.strip() else ""
        seconds = parse_duration_loose(raw_time)
        if seconds is None or seconds <= 0 or seconds > _MAX_SECONDS:
            await ctx.reply(ctx.t("bomb.usage_reply"))
            return

        await ctx.delete_command_message()
        asyncio.create_task(
            _explode(ctx.bot, ctx.connection_id, target.message_id, seconds)
        )
        return

    parts = ctx.args.split(maxsplit=1)
    if len(parts) < 2:
        await ctx.reply(ctx.t("bomb.usage_full"))
        return

    raw_time, text = parts
    seconds = parse_duration_loose(raw_time)
    if seconds is None or seconds <= 0 or seconds > _MAX_SECONDS:
        await ctx.reply(ctx.t("bomb.invalid_time"))
        return

    await ctx.delete_command_message()
    sent = await ctx.reply(text)

    asyncio.create_task(_explode(ctx.bot, ctx.connection_id, sent.message_id, seconds))
