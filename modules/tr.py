import asyncio

from deep_translator import GoogleTranslator

from core.context import CommandContext
from core.registry import command


@command(name="tr", module="tr", description="Переводит текст на нужный язык")
async def cmd_tr(ctx: CommandContext):
    parts = ctx.args.split(maxsplit=1)
    if len(parts) < 2:
        await ctx.reply(ctx.t("tr.usage"))
        return

    lang, text = parts
    await ctx.delete_command_message()

    try:
        translated = await asyncio.to_thread(
            lambda: GoogleTranslator(source="auto", target=lang.lower()).translate(text)
        )
    except Exception:
        await ctx.reply(ctx.t("tr.failed"))
        return

    await ctx.reply(translated)
