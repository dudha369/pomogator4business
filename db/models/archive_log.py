from tortoise import fields
from tortoise.models import Model


class ArchiveLog(Model):
    log_id = fields.BigIntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()
    event = fields.CharField(max_length=32)
    old_text = fields.TextField(null=True)
    new_text = fields.TextField(null=True)
    created_at = fields.BigIntField()

    class Meta:
        table = "archive_log"
