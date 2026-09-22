from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from core import database as db
from core.i18n import t
from core.registry import command

router = Router(name="chk")

_SIZE = 8
_DIRECTIONS_KING = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
_DIRECTIONS_WHITE = [(-1, -1), (-1, 1)]
_DIRECTIONS_BLACK = [(1, -1), (1, 1)]

_SYMBOLS = {
    ".": "·",
    " ": " ",
    "w": "⚪",
    "W": "⚪👑",
    "b": "⚫",
    "B": "⚫👑",
}


def is_dark(row, col):
    return (row + col) % 2 == 1


def initial_board():
    cells = []
    for row in range(_SIZE):
        for col in range(_SIZE):
            if not is_dark(row, col):
                cells.append(" ")
            elif row <= 2:
                cells.append("b")
            elif row >= 5:
                cells.append("w")
            else:
                cells.append(".")
    return "".join(cells)


def _owner(cell):
    if cell in ("w", "W"):
        return "w"
    if cell in ("b", "B"):
        return "b"
    return None


def _is_king(cell):
    return cell in ("W", "B")


def legal_moves_for(board, index, color):
    row, col = divmod(index, _SIZE)
    piece = board[index]
    if _owner(piece) != color:
        return []

    directions = (
        _DIRECTIONS_KING
        if _is_king(piece)
        else (_DIRECTIONS_WHITE if color == "w" else _DIRECTIONS_BLACK)
    )

    moves = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        if not (0 <= nr < _SIZE and 0 <= nc < _SIZE):
            continue
        n_idx = nr * _SIZE + nc
        n_cell = board[n_idx]

        if n_cell == ".":
            moves.append((n_idx, None))
        elif _owner(n_cell) not in (None, color):
            jr, jc = nr + dr, nc + dc
            if 0 <= jr < _SIZE and 0 <= jc < _SIZE:
                j_idx = jr * _SIZE + jc
                if board[j_idx] == ".":
                    moves.append((j_idx, n_idx))

    return moves


def has_any_move(board, color):
    for idx, cell in enumerate(board):
        if _owner(cell) == color and legal_moves_for(board, idx, color):
            return True
    return False


def apply_move(board, from_idx, to_idx, captured_idx):
    cells = list(board)
    piece = cells[from_idx]
    cells[from_idx] = "."
    if captured_idx is not None:
        cells[captured_idx] = "."

    to_row = to_idx // _SIZE
    if piece == "w" and to_row == 0:
        piece = "W"
    elif piece == "b" and to_row == _SIZE - 1:
        piece = "B"

    cells[to_idx] = piece
    return "".join(cells)


def count_pieces(board, color):
    return sum(1 for cell in board if _owner(cell) == color)


def _build_keyboard(board, selected):
    rows = []
    for r in range(_SIZE):
        row_buttons = []
        for c in range(_SIZE):
            idx = r * _SIZE + c
            cell = board[idx]
            if cell == " ":
                text = " "
                callback_data = "chk:noop"
            else:
                text = _SYMBOLS[cell]
                if selected == idx:
                    text += "🔲"
                callback_data = f"chk:{idx}"
            row_buttons.append(
                InlineKeyboardButton(text=text, callback_data=callback_data)
            )
        rows.append(row_buttons)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _build_text(locale, game, winner):
    w_name = game["player_w_name"] or "?"
    b_name = game["player_b_name"] or "?"
    header = t("chk.header", locale, w_name=w_name, b_name=b_name)

    if winner:
        color_name = t("chk.white", locale) if winner == "w" else t("chk.black", locale)
        status = t("chk.win", locale, color=color_name)
    else:
        current = (
            t("chk.white", locale) if game["turn"] == "w" else t("chk.black", locale)
        )
        status = t("chk.turn", locale, color=current)

    return header + "\n\n" + status


@command(name="chk", module="chk", description="Шашки", owner_only=False)
async def cmd_chk(ctx):
    starter_name = ctx.message.from_user.full_name if ctx.message.from_user else "White"

    await db.save_chk_game(
        ctx.connection_id,
        ctx.chat_id,
        board=initial_board(),
        turn="w",
        player_w_id=ctx.message.from_user.id,
        player_w_name=starter_name,
        player_b_id=None,
        player_b_name=None,
        selected=None,
        status="active",
        message_id=None,
    )

    game = await db.get_chk_game(ctx.connection_id, ctx.chat_id)
    text = _build_text(ctx.locale, game, None)
    keyboard = _build_keyboard(game["board"], None)

    await ctx.delete_command_message()
    sent = await ctx.answer(text, reply_markup=keyboard)
    await db.save_chk_game(ctx.connection_id, ctx.chat_id, message_id=sent.message_id)


@router.callback_query(F.data.startswith("chk:"))
async def on_chk_callback(call: CallbackQuery):
    action = call.data.split(":", 1)[1]
    if action == "noop":
        await call.answer()
        return

    business_connection_id = call.message.business_connection_id
    chat_id = call.message.chat.id

    game = await db.get_chk_game(business_connection_id, chat_id)
    if not game or game["status"] != "active":
        await call.answer()
        return

    connection = await db.get_connection(business_connection_id)
    locale = await db.get_locale(connection["owner_id"]) if connection else "ru"

    user_id = call.from_user.id

    if user_id == game["player_w_id"]:
        color = "w"
    elif game["player_b_id"] is None and user_id != game["player_w_id"]:
        color = "b"
        await db.save_chk_game(
            business_connection_id,
            chat_id,
            player_b_id=user_id,
            player_b_name=call.from_user.full_name,
        )
        game = await db.get_chk_game(business_connection_id, chat_id)
    elif user_id == game["player_b_id"]:
        color = "b"
    else:
        await call.answer(t("chk.not_your_game", locale), show_alert=True)
        return

    if color != game["turn"]:
        await call.answer(t("chk.not_your_turn", locale), show_alert=True)
        return

    idx = int(action)
    board = game["board"]
    selected = game["selected"]

    if selected is None:
        if _owner(board[idx]) != color:
            await call.answer()
            return
        if not legal_moves_for(board, idx, color):
            await call.answer(t("chk.no_moves", locale), show_alert=True)
            return
        await db.save_chk_game(business_connection_id, chat_id, selected=idx)
        await call.message.edit_reply_markup(reply_markup=_build_keyboard(board, idx))
        await call.answer()
        return

    if idx == selected:
        await db.save_chk_game(business_connection_id, chat_id, selected=None)
        await call.message.edit_reply_markup(reply_markup=_build_keyboard(board, None))
        await call.answer()
        return

    if _owner(board[idx]) == color:
        if not legal_moves_for(board, idx, color):
            await call.answer(t("chk.no_moves", locale), show_alert=True)
            return
        await db.save_chk_game(business_connection_id, chat_id, selected=idx)
        await call.message.edit_reply_markup(reply_markup=_build_keyboard(board, idx))
        await call.answer()
        return

    moves = legal_moves_for(board, selected, color)
    move = next((m for m in moves if m[0] == idx), None)
    if not move:
        await call.answer(t("chk.invalid_move", locale), show_alert=True)
        return

    _, captured_idx = move
    new_board = apply_move(board, selected, idx, captured_idx)
    opponent = "b" if color == "w" else "w"

    winner = None
    if count_pieces(new_board, opponent) == 0 or not has_any_move(new_board, opponent):
        winner = color

    status = "finished" if winner else "active"
    next_turn = opponent if not winner else game["turn"]

    await db.save_chk_game(
        business_connection_id,
        chat_id,
        board=new_board,
        turn=next_turn,
        selected=None,
        status=status,
    )
    game = await db.get_chk_game(business_connection_id, chat_id)

    await call.message.edit_text(
        _build_text(locale, game, winner),
        reply_markup=_build_keyboard(new_board, None),
    )
    await call.answer()
