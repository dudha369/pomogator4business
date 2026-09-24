from tortoise import fields
from tortoise.models import Model


class MessageLog(Model):
    log_id = fields.BigIntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()

    class Meta:
        table = "message_log"
        indexes = (("connection_id", "chat_id", "log_id"),)


async def log_message(connection_id, chat_id, message_id):
    await MessageLog.create(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    )


async def pop_recent_message_ids(connection_id, chat_id, count):
    rows = (
        await MessageLog.filter(connection_id=connection_id, chat_id=chat_id)
        .order_by("-log_id")
        .limit(count)
        .values("log_id", "message_id")
    )
    log_ids = [row["log_id"] for row in rows]
    message_ids = [row["message_id"] for row in rows]
    if log_ids:
        await MessageLog.filter(log_id__in=log_ids).delete()
    return message_ids
