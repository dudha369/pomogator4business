from tortoise import fields
from tortoise.models import Model

from db.models._game_state import get_game, save_game


class G2048Game(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    board = fields.TextField(default="")
    score = fields.IntField(default=0)
    status = fields.CharField(max_length=16, default="active")
    player_id = fields.BigIntField(null=True)
    message_id = fields.BigIntField(null=True)

    class Meta:
        table = "g2048_games"
        unique_together = (("connection_id", "chat_id"),)


_DEFAULTS = {
    "board": "",
    "score": 0,
    "status": "active",
    "player_id": None,
    "message_id": None,
}


async def save_g2048_game(connection_id, chat_id, **fields):
    await save_game(G2048Game, connection_id, chat_id, _DEFAULTS, fields)


async def get_g2048_game(connection_id, chat_id):
    return await get_game(G2048Game, connection_id, chat_id)
