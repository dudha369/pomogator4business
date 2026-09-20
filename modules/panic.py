from core.context import CommandContext
from core.registry import command
from core import database as db

_MAX_COUNT = 1000
_CHUNK_SIZE = 100


def _chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


@command(
    name="panic",
    aliases=["del"],
    module="panic",
    description="Удаляет последние N сообщений в чате",
)
async def cmd_panic(ctx: CommandContext):
    parts = ctx.args.split()
    if not parts or not parts[0].isdigit():
        await ctx.bot.send_message(
            chat_id=ctx.connection["owner_chat_id"],
            text=ctx.t("panic.usage_dm"),
        )
        return

    count = min(int(parts[0]), _MAX_COUNT)
    if count <= 0:
        return

    ids = await db.pop_recent_message_ids(ctx.connection_id, ctx.chat_id, count)
    for chunk in _chunks(ids, _CHUNK_SIZE):
        try:
            await ctx.bot.delete_business_messages(
                business_connection_id=ctx.connection_id,
                message_ids=chunk,
            )
        except Exception:
            pass
