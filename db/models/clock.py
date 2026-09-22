from tortoise import fields
from tortoise.models import Model


class ClockPack(Model):
    pack_index = fields.IntField(pk=True, generated=False)
    pack_name = fields.CharField(max_length=255)
    uploaded_count = fields.IntField(default=0)
    completed = fields.BooleanField(default=False)

    class Meta:
        table = "clock_packs"


class ClockEmoji(Model):
    time_key = fields.CharField(max_length=16, pk=True)
    pack_index = fields.IntField()
    custom_emoji_id = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "clock_emojis"
