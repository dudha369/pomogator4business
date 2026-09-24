from tortoise import fields
from tortoise.models import Model


class MessageHistory(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()
    is_owner = fields.BooleanField()
    text = fields.TextField(null=True)
    created_at = fields.BigIntField()

    class Meta:
        table = "message_history"
        unique_together = (("connection_id", "chat_id", "message_id"),)
        indexes = (("connection_id", "chat_id", "created_at"),)


async def save_history(connection_id, chat_id, message_id, is_owner, text, created_at):
    obj, created = await MessageHistory.get_or_create(
        connection_id=connection_id,
        chat_id=chat_id,
        message_id=message_id,
        defaults={
            "is_owner": bool(is_owner),
            "text": text,
            "created_at": created_at,
        },
    )
    if not created:
        obj.text = text
        await obj.save(update_fields=["text"])


async def get_history_text(connection_id, chat_id, message_id):
    rows = await MessageHistory.filter(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    ).values("text")
    return rows[0]["text"] if rows else None


async def get_history_entry(connection_id, chat_id, message_id):
    """Как get_history_text, но возвращает всю строку (в т.ч. is_owner)."""
    rows = await MessageHistory.filter(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    ).values()
    return rows[0] if rows else None


async def delete_history(connection_id, chat_id, message_id):
    await MessageHistory.filter(
        connection_id=connection_id, chat_id=chat_id, message_id=message_id
    ).delete()


async def get_recent_history(connection_id, chat_id, limit):
    rows = (
        await MessageHistory.filter(connection_id=connection_id, chat_id=chat_id)
        .order_by("-created_at")
        .limit(limit)
        .values()
    )
    return list(reversed(rows))
