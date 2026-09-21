import re
import time

from aiogram import Bot as AiogramBot
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from core import database as db
from core.crypto import encrypt_token
from core.i18n import t
from core.mirror_manager import mirror_manager

router = Router(name="mirror_setup")

_TOKEN_PATTERN = re.compile(r"^\d+:[A-Za-z0-9_-]{30,50}$")


class MirrorState(StatesGroup):
    waiting_for_token = State()


@router.message(Command("mirror"))
async def cmd_mirror(message: Message, state: FSMContext):
    locale = await db.get_locale(message.from_user.id)
    existing = await db.get_mirror(message.from_user.id)
    if existing and existing["is_active"]:
        await message.answer(
            t("mirror.already_connected", locale, username=existing["bot_username"])
        )
        return

    await message.answer(t("mirror.onboarding", locale))
    await state.set_state(MirrorState.waiting_for_token)


@router.message(Command("unmirror"))
async def cmd_unmirror(message: Message):
    locale = await db.get_locale(message.from_user.id)
    existing = await db.get_mirror(message.from_user.id)
    if not existing:
        await message.answer(t("mirror.not_connected", locale))
        return

    await mirror_manager.stop_mirror(message.from_user.id)
    await db.delete_mirror(message.from_user.id)
    await message.answer(t("mirror.disconnected", locale))


@router.message(Command("cancel"), StateFilter(MirrorState.waiting_for_token))
async def cmd_cancel(message: Message, state: FSMContext):
    locale = await db.get_locale(message.from_user.id)
    await state.clear()
    await message.answer(t("mirror.cancelled", locale))


@router.message(StateFilter(MirrorState.waiting_for_token))
async def on_token_received(message: Message, state: FSMContext):
    locale = await db.get_locale(message.from_user.id)
    token = message.text.strip() if message.text else ""

    if not _TOKEN_PATTERN.match(token):
        await message.answer(t("mirror.invalid_token_format", locale))
        return

    test_bot = AiogramBot(token=token)
    try:
        me = await test_bot.get_me()
    except Exception:
        await message.answer(t("mirror.connection_failed", locale))
        return
    finally:
        await test_bot.session.close()

    await db.save_mirror(
        message.from_user.id, encrypt_token(token), me.id, me.username, int(time.time())
    )
    await state.clear()

    await mirror_manager.start_mirror(message.from_user.id, token)

    await message.answer(t("mirror.connected_success", locale, username=me.username))
