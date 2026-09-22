from tortoise import fields
from tortoise.models import Model


class DisabledModule(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    module = fields.CharField(max_length=64)

    class Meta:
        table = "disabled_modules"
        unique_together = (("connection_id", "module"),)
