from tortoise import fields
from tortoise.models import Model

from db.models._game_state import get_game, save_game


class HangmanGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.CharField(max_length=64, default="")
    guessed_letters = fields.TextField(default="[]")
    mistakes = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "hangman_games"
        unique_together = (("connection_id", "chat_id"),)


_DEFAULTS = {
    "secret": "",
    "guessed_letters": "[]",
    "mistakes": 0,
    "status": "active",
    "message_id": None,
}


async def save_hangman_game(connection_id, chat_id, **fields):
    await save_game(HangmanGame, connection_id, chat_id, _DEFAULTS, fields)


async def get_hangman_game(connection_id, chat_id):
    return await get_game(HangmanGame, connection_id, chat_id)
