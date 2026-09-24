from tortoise import fields
from tortoise.models import Model


class MirrorBot(Model):
    owner_id = fields.BigIntField(pk=True, generated=False)
    token_encrypted = fields.BinaryField()
    bot_id = fields.BigIntField(null=True)
    bot_username = fields.CharField(max_length=255, null=True)
    created_at = fields.BigIntField()
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "mirror_bots"


async def save_mirror(owner_id, token_encrypted, bot_id, bot_username, created_at):
    await MirrorBot.update_or_create(
        owner_id=owner_id,
        defaults={
            "token_encrypted": token_encrypted,
            "bot_id": bot_id,
            "bot_username": bot_username,
            "created_at": created_at,
            "is_active": True,
        },
    )


async def get_mirror(owner_id):
    rows = await MirrorBot.filter(owner_id=owner_id).values()
    return rows[0] if rows else None


async def get_all_active_mirrors():
    return await MirrorBot.filter(is_active=True).values()


async def delete_mirror(owner_id):
    await MirrorBot.filter(owner_id=owner_id).delete()
