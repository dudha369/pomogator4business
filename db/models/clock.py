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


async def get_clock_pack(pack_index):
    rows = await ClockPack.filter(pack_index=pack_index).values()
    return rows[0] if rows else None


async def upsert_clock_pack(pack_index, pack_name, uploaded_count, completed):
    await ClockPack.update_or_create(
        pack_index=pack_index,
        defaults={
            "pack_name": pack_name,
            "uploaded_count": uploaded_count,
            "completed": bool(completed),
        },
    )


async def save_clock_emoji(time_key, pack_index, custom_emoji_id):
    await ClockEmoji.update_or_create(
        time_key=time_key,
        defaults={"pack_index": pack_index, "custom_emoji_id": custom_emoji_id},
    )


async def get_clock_emoji(time_key):
    rows = await ClockEmoji.filter(time_key=time_key).values("custom_emoji_id")
    return rows[0]["custom_emoji_id"] if rows else None


async def count_clock_emojis():
    return await ClockEmoji.all().count()
