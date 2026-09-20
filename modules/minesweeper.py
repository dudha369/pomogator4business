import random

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from core import database as db
from core.i18n import t
from core.registry import command

router = Router(name="ms")

_AUTO_BOMBS = {6: 6, 8: 9, 9: 12}
_NUMBER_EMOJI = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣"}


def resolve_bomb_count(size, bomb_mode):
    if bomb_mode == "5":
        return 5
    if bomb_mode == "8":
        return 8
    return _AUTO_BOMBS.get(size, 6)


def generate_mines(size, bomb_count, rng=None):
    rng = rng or random
    total = size * size
    return set(rng.sample(range(total), min(bomb_count, total)))


def adjacent_count(size, mines, index):
    row, col = divmod(index, size)
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < size and 0 <= nc < size and (nr * size + nc) in mines:
                count += 1
    return count


def flood_reveal(size, mines, revealed, start_index):
    if start_index in revealed:
        return
    stack = [start_index]
    while stack:
        idx = stack.pop()
        if idx in revealed:
            continue
        revealed.add(idx)
        if idx in mines:
            continue
        if adjacent_count(size, mines, idx) == 0:
            row, col = divmod(idx, size)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        nidx = nr * size + nc
                        if nidx not in revealed and nidx not in mines:
                            stack.append(nidx)


def is_win(size, mines, revealed):
    return len(revealed - mines) == size * size - len(mines)


def _mines_from_json(raw):
    import json
    return set(json.loads(raw))


def _mines_to_json(mines):
    import json
    return json.dumps(list(mines))


def _revealed_from_str(raw, size):
    return {i for i, ch in enumerate(raw) if ch == "1"}


def _revealed_to_str(revealed, size):
    return "".join("1" if i in revealed else "0" for i in range(size * size))


def _settings_keyboard(game):
    rows = []

    size_row = []
    for s in (6, 8, 9):
        mark = "✅ " if game["size"] == s else ""
        size_row.append(InlineKeyboardButton(text=f"{mark}{s}x{s}", callback_data=f"ms:size:{s}"))
    rows.append(size_row)

    bomb_row = []
    for mode, label in (("5", "5"), ("8", "8"), ("auto", "Auto")):
        mark = "✅ " if game["bomb_mode"] == mode else ""
        bomb_row.append(InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"ms:bombs:{mode}"))
    rows.append(bomb_row)

    coop_mark = "✅" if game["coop"] else "☑️"
    rows.append([InlineKeyboardButton(text=f"{coop_mark} co-op", callback_data="ms:coop:toggle")])
    rows.append([InlineKeyboardButton(text="🎮", callback_data="ms:start")])
    rows.append([InlineKeyboardButton(text="🗑", callback_data="ms:stop")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def _game_keyboard(size, mines, revealed, exploded_idx, finished):
    rows = []
    for r in range(size):
        row_buttons = []
        for c in range(size):
            idx = r * size + c
            if idx in revealed or finished:
                if idx in mines:
                    text = "💥" if idx == exploded_idx else "💣"
                else:
                    count = adjacent_count(size, mines, idx)
                    text = _NUMBER_EMOJI.get(count, "·")
                callback_data = "ms:noop"
            else:
                text = "⬜"
                callback_data = f"ms:cell:{idx}"
            row_buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        rows.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=rows)


@command(name="ms", module="ms", description="Сапёр", owner_only=False)
async def cmd_ms(ctx):
    starter_name = ctx.message.from_user.full_name if ctx.message.from_user else "?"

    await db.save_ms_game(
        ctx.connection_id, ctx.chat_id,
        size=6, bomb_mode="auto", coop=0,
        mines="[]", revealed="", starter_id=ctx.message.from_user.id,
        starter_name=starter_name, phase="settings", message_id=None,
    )

    game = await db.get_ms_game(ctx.connection_id, ctx.chat_id)
    text = t("ms.settings_title", ctx.locale)
    keyboard = _settings_keyboard(game)

    await ctx.delete_command_message()
    sent = await ctx.reply(text, reply_markup=keyboard)
    await db.save_ms_game(ctx.connection_id, ctx.chat_id, message_id=sent.message_id)


@router.callback_query(F.data.startswith("ms:"))
async def on_ms_callback(call: CallbackQuery):
    parts = call.data.split(":")
    action = parts[1]

    if action == "noop":
        await call.answer()
        return

    business_connection_id = call.message.business_connection_id
    chat_id = call.message.chat.id

    game = await db.get_ms_game(business_connection_id, chat_id)
    if not game:
        await call.answer()
        return

    connection = await db.get_connection(business_connection_id)
    locale = await db.get_locale(connection["owner_id"]) if connection else "ru"

    if action in ("size", "bombs", "coop", "start", "stop"):
        if call.from_user.id != game["starter_id"]:
            await call.answer(t("ms.not_starter", locale), show_alert=True)
            return

    if game["phase"] == "settings":
        if action == "size":
            await db.save_ms_game(business_connection_id, chat_id, size=int(parts[2]))
        elif action == "bombs":
            await db.save_ms_game(business_connection_id, chat_id, bomb_mode=parts[2])
        elif action == "coop":
            await db.save_ms_game(business_connection_id, chat_id, coop=0 if game["coop"] else 1)
        elif action == "stop":
            await call.message.edit_text(t("ms.cancelled", locale))
            await call.answer()
            return
        elif action == "start":
            size = game["size"]
            bomb_count = resolve_bomb_count(size, game["bomb_mode"])
            mines = generate_mines(size, bomb_count)
            await db.save_ms_game(
                business_connection_id, chat_id,
                mines=_mines_to_json(mines),
                revealed=_revealed_to_str(set(), size),
                phase="active",
            )
            game = await db.get_ms_game(business_connection_id, chat_id)
            await call.message.edit_text(
                t("ms.playing", locale, size=size, bombs=bomb_count),
                reply_markup=_game_keyboard(size, mines, set(), None, False),
            )
            await call.answer()
            return
        else:
            await call.answer()
            return

        game = await db.get_ms_game(business_connection_id, chat_id)
        await call.message.edit_reply_markup(reply_markup=_settings_keyboard(game))
        await call.answer()
        return

    if game["phase"] != "active":
        await call.answer()
        return

    if action == "stop":
        await db.save_ms_game(business_connection_id, chat_id, phase="finished")
        await call.message.edit_text(t("ms.cancelled", locale))
        await call.answer()
        return

    if action != "cell":
        await call.answer()
        return

    if not game["coop"] and call.from_user.id != game["starter_id"]:
        await call.answer(t("ms.not_starter", locale), show_alert=True)
        return

    idx = int(parts[2])
    size = game["size"]
    mines = _mines_from_json(game["mines"])
    revealed = _revealed_from_str(game["revealed"], size)

    if idx in revealed:
        await call.answer()
        return

    if idx in mines:
        revealed.add(idx)
        await db.save_ms_game(
            business_connection_id, chat_id,
            revealed=_revealed_to_str(revealed, size), phase="finished",
        )
        await call.message.edit_text(
            t("ms.lost", locale),
            reply_markup=_game_keyboard(size, mines, revealed, idx, True),
        )
        await call.answer()
        return

    flood_reveal(size, mines, revealed, idx)

    if is_win(size, mines, revealed):
        await db.save_ms_game(
            business_connection_id, chat_id,
            revealed=_revealed_to_str(revealed, size), phase="finished",
        )
        await call.message.edit_text(
            t("ms.won", locale),
            reply_markup=_game_keyboard(size, mines, revealed, None, True),
        )
        await call.answer()
        return

    await db.save_ms_game(business_connection_id, chat_id, revealed=_revealed_to_str(revealed, size))
    await call.message.edit_reply_markup(
        reply_markup=_game_keyboard(size, mines, revealed, None, False)
    )
    await call.answer()
