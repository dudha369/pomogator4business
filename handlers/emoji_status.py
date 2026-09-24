from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from config import settings
from core import database as db
from core.i18n import t

router = Router(name="emoji_status")


@router.message(Command("emojistatus"))
async def cmd_emoji_status(message: Message):
    owner_id = message.from_user.id
    locale = await db.get_locale(owner_id)
    granted = await db.is_emoji_status_granted(owner_id)

    if not granted:
        if not settings.WEBAPP_URL:
            await message.answer(t("emoji_status.not_configured", locale))
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=t("emoji_status.open_button", locale),
                        web_app=WebAppInfo(url=settings.WEBAPP_URL),
                    )
                ]
            ]
        )
        await message.answer(
            t("emoji_status.request_prompt", locale), reply_markup=keyboard
        )
        return

    enabled = await db.is_emoji_status_enabled(owner_id)
    new_state = not enabled
    await db.set_emoji_status_enabled(owner_id, new_state)
    status = (
        t("emoji_status.status_on", locale)
        if new_state
        else t("emoji_status.status_off", locale)
    )
    await message.answer(t("emoji_status.toggled", locale, status=status))
