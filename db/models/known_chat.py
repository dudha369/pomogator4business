from tortoise import fields
from tortoise.models import Model


class KnownChat(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()

    class Meta:
        table = "known_chats"
        unique_together = (("connection_id", "chat_id"),)
