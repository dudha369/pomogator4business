import os
import tempfile

from core.context import CommandContext
from core.registry import command
from core.stt import transcribe_audio


def _extract_file_id(message):
    if message.voice:
        return message.voice.file_id
    if message.video_note:
        return message.video_note.file_id
    return None


@command(name="stt", module="stt", description="Распознаёт речь из ГС или видео-кружка")
async def cmd_stt(ctx: CommandContext):
    target = ctx.message.reply_to_message
    file_id = _extract_file_id(target) if target else None

    if not file_id:
        await ctx.usage_error(ctx.t("stt.usage"))
        return

    file = await ctx.bot.get_file(file_id)
    buffer = await ctx.bot.download_file(file.file_path)
    data = buffer.read()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        await ctx.reply(ctx.t("stt.processing"))
        text = await transcribe_audio(tmp_path)
    except Exception:
        await ctx.reply(ctx.t("stt.failed"))
        return
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if not text:
        await ctx.reply(ctx.t("stt.empty"))
        return

    await ctx.reply(text)
