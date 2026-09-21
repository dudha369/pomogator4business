import asyncio

from aiogram import Bot, F, Router
from aiogram.types import Message

router = Router(name="mirror_spam")

_MAX_COUNT = 200
_MIN_DELAY = 0.1
_MAX_DELAY = 60
_DEFAULT_STEP_DELAY = 0.3


@router.message(F.text.regexp(r"^\.spam(\s|$)"))
async def cmd_spam(message: Message, bot: Bot):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer("Формат: .spam [кол-во] [текст]\nПример: .spam 10 Привет")
        return

    count = min(int(parts[1]), _MAX_COUNT)
    text = parts[2]
    if count <= 0:
        return

    for _ in range(count):
        await bot.send_message(chat_id=message.chat.id, text=text)
        await asyncio.sleep(0.05)


@router.message(F.text.regexp(r"^\.dspam(\s|$)"))
async def cmd_dspam(message: Message, bot: Bot):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer(
            "Формат: .dspam [задержка] [кол-во] [текст]\nПример: .dspam 2 10 Привет"
        )
        return

    try:
        delay = float(parts[1])
    except ValueError:
        await message.answer("Задержка должна быть числом от 0.1 до 60 секунд.")
        return

    if not parts[2].isdigit():
        await message.answer("Количество должно быть числом.")
        return

    delay = max(_MIN_DELAY, min(delay, _MAX_DELAY))
    count = min(int(parts[2]), _MAX_COUNT)
    text = parts[3]
    if count <= 0:
        return

    for _ in range(count):
        await bot.send_message(chat_id=message.chat.id, text=text)
        await asyncio.sleep(delay)


@router.message(F.text.regexp(r"^\.wspam(\s|$)"))
async def cmd_wspam(message: Message, bot: Bot):
    text = message.text[len(".wspam") :].strip()
    if not text:
        await message.answer("Формат: .wspam [предложение]")
        return

    words = text.split()[:_MAX_COUNT]
    for word in words:
        await bot.send_message(chat_id=message.chat.id, text=word)
        await asyncio.sleep(_DEFAULT_STEP_DELAY)


@router.message(F.text.regexp(r"^\.lspam(\s|$)"))
async def cmd_lspam(message: Message, bot: Bot):
    text = message.text[len(".lspam") :].strip()
    if not text:
        await message.answer("Формат: .lspam [слово или предложение]")
        return

    chars = [char for char in text if not char.isspace()][:_MAX_COUNT]
    for char in chars:
        await bot.send_message(chat_id=message.chat.id, text=char)
        await asyncio.sleep(_DEFAULT_STEP_DELAY)
