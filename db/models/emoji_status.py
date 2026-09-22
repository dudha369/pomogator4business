from tortoise import fields
from tortoise.models import Model


class EmojiStatusSetting(Model):
    owner_id = fields.BigIntField(pk=True, generated=False)
    granted = fields.BooleanField(default=False)
    enabled = fields.BooleanField(default=False)

    class Meta:
        table = "emoji_status_settings"
