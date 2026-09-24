from tortoise import fields
from tortoise.models import Model

from db.models._game_state import get_game, save_game


class CityGame(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    used_words = fields.TextField(default="[]")
    next_letter = fields.CharField(max_length=4, null=True)
    status = fields.CharField(max_length=16, default="active")

    class Meta:
        table = "city_games"
        unique_together = (("connection_id", "chat_id"),)


_DEFAULTS = {"used_words": "[]", "next_letter": None, "status": "active"}


async def save_city_game(connection_id, chat_id, **fields):
    await save_game(CityGame, connection_id, chat_id, _DEFAULTS, fields)


async def get_city_game(connection_id, chat_id):
    return await get_game(CityGame, connection_id, chat_id)
