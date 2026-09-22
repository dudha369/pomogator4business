from tortoise import fields
from tortoise.models import Model


class Connection(Model):
    connection_id = fields.CharField(max_length=255, pk=True)
    owner_id = fields.BigIntField()
    owner_chat_id = fields.BigIntField()
    owner_name = fields.CharField(max_length=255, null=True)
    owner_username = fields.CharField(max_length=255, null=True)
    is_enabled = fields.BooleanField(default=True)
    prefix = fields.CharField(max_length=8, default=".")
    rights_json = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "connections"
