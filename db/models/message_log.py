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
