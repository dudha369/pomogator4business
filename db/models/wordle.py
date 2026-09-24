from tortoise import fields
from tortoise.models import Model

from db.models._game_state import get_game, save_game


class WordleGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.CharField(max_length=32, default="")
    guesses = fields.TextField(default="[]")
    status = fields.CharField(max_length=16, default="active")
    message_id = fields.BigIntField(null=True)
    starter_id = fields.BigIntField(null=True)

    class Meta:
        table = "wordle_games"
        unique_together = (("connection_id", "chat_id"),)


_DEFAULTS = {
    "secret": "",
    "guesses": "[]",
    "status": "active",
    "message_id": None,
    "starter_id": None,
}


async def save_wordle_game(connection_id, chat_id, **fields):
    await save_game(WordleGame, connection_id, chat_id, _DEFAULTS, fields)


async def get_wordle_game(connection_id, chat_id):
    return await get_game(WordleGame, connection_id, chat_id)
