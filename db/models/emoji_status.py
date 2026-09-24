from tortoise import fields
from tortoise.models import Model


class EmojiStatusSetting(Model):
    owner_id = fields.BigIntField(pk=True, generated=False)
    granted = fields.BooleanField(default=False)
    enabled = fields.BooleanField(default=False)

    class Meta:
        table = "emoji_status_settings"


async def set_emoji_status_granted(owner_id, granted):
    obj, created = await EmojiStatusSetting.get_or_create(
        owner_id=owner_id, defaults={"granted": bool(granted), "enabled": False}
    )
    if not created:
        obj.granted = bool(granted)
        await obj.save(update_fields=["granted"])


async def is_emoji_status_granted(owner_id):
    rows = await EmojiStatusSetting.filter(owner_id=owner_id).values("granted")
    return bool(rows and rows[0]["granted"])


async def set_emoji_status_enabled(owner_id, enabled):
    obj, created = await EmojiStatusSetting.get_or_create(
        owner_id=owner_id, defaults={"granted": False, "enabled": bool(enabled)}
    )
    if not created:
        obj.enabled = bool(enabled)
        await obj.save(update_fields=["enabled"])


async def is_emoji_status_enabled(owner_id):
    rows = await EmojiStatusSetting.filter(owner_id=owner_id).values("enabled")
    return bool(rows and rows[0]["enabled"])


async def get_active_emoji_status_owners():
    return await EmojiStatusSetting.filter(enabled=True, granted=True).values_list(
        "owner_id", flat=True
    )
