from tortoise import fields
from tortoise.models import Model


class EchoChat(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()

    class Meta:
        table = "echo_chats"
        unique_together = (("connection_id", "chat_id"),)


async def is_echo_enabled(connection_id, chat_id):
    return await EchoChat.filter(connection_id=connection_id, chat_id=chat_id).exists()


async def toggle_echo(connection_id, chat_id):
    enabled = await is_echo_enabled(connection_id, chat_id)
    if enabled:
        await EchoChat.filter(connection_id=connection_id, chat_id=chat_id).delete()
    else:
        await EchoChat.get_or_create(connection_id=connection_id, chat_id=chat_id)
    return not enabled
