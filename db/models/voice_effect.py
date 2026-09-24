from tortoise import fields
from tortoise.models import Model


class VoiceEffect(Model):
    id = fields.IntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    chat_id = fields.BigIntField()
    effect = fields.CharField(max_length=64)

    class Meta:
        table = "voice_effects"
        unique_together = (("connection_id", "chat_id"),)


async def get_voice_effect(connection_id, chat_id):
    rows = await VoiceEffect.filter(
        connection_id=connection_id, chat_id=chat_id
    ).values("effect")
    return rows[0]["effect"] if rows else None


async def set_voice_effect(connection_id, chat_id, effect):
    if effect is None:
        await VoiceEffect.filter(connection_id=connection_id, chat_id=chat_id).delete()
    else:
        await VoiceEffect.update_or_create(
            connection_id=connection_id, chat_id=chat_id, defaults={"effect": effect}
        )
