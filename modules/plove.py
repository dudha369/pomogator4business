from core.context import CommandContext
from core.registry import command
from modules.type_ import typewriter


@command(
    name="plove", module="plove", description="Печатает текст в окружении сердечек"
)
async def cmd_plove(ctx: CommandContext):
    if not ctx.args.strip():
        return

    await ctx.delete_command_message()
    decorated = f"❤️ {ctx.args} ❤️"
    await typewriter(ctx.bot, ctx.connection, ctx.chat_id, decorated, "❤️")
