from tortoise import fields
from tortoise.models import Model

from db.models._game_state import get_game, save_game


class GuessGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    secret = fields.IntField(default=1)
    max_value = fields.IntField(default=100)
    attempts = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")

    class Meta:
        table = "guess_games"
        unique_together = (("connection_id", "chat_id"),)


_DEFAULTS = {"secret": 1, "max_value": 100, "attempts": 0, "status": "active"}


async def save_guess_game(connection_id, chat_id, **fields):
    await save_game(GuessGame, connection_id, chat_id, _DEFAULTS, fields)


async def get_guess_game(connection_id, chat_id):
    return await get_game(GuessGame, connection_id, chat_id)
