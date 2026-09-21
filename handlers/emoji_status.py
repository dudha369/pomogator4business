import json

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from config import WEBAPP_URL
from core import database as db
from core.i18n import t

router = Router(name="emoji_status")


@router.message(Command("emojistatus"))
async def cmd_emoji_status(message: Message):
    owner_id = message.from_user.id
    locale = await db.get_locale(owner_id)
    granted = await db.is_emoji_status_granted(owner_id)

    if not granted:
        if not WEBAPP_URL:
            await message.answer(t("emoji_status.not_configured", locale))
            return

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=t("emoji_status.open_button", locale),
                        web_app=WebAppInfo(url=WEBAPP_URL),
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
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


@router.message(F.web_app_data)
async def on_web_app_data(message: Message):
    owner_id = message.from_user.id
    locale = await db.get_locale(owner_id)
    try:
        payload = json.loads(message.web_app_data.data)
    except Exception:
        return

    granted = bool(payload.get("emoji_status_access"))
    await db.set_emoji_status_granted(owner_id, granted)

    if granted:
        await db.set_emoji_status_enabled(owner_id, True)
        await message.answer(
            t("emoji_status.granted_enabled", locale),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            t("emoji_status.denied", locale), reply_markup=ReplyKeyboardRemove()
        )
