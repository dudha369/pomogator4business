from tortoise import fields
from tortoise.models import Model


class StoryAutopost(Model):
    """Название унаследовано от старой (уже убранной) очереди на отложенный
    постинг — сейчас это просто флаг для /story: публиковать историю сразу
    (enabled=True) или прислать владельцу файлы в ЛС (enabled=False). Поле
    last_post_date больше не используется в коде, но оставлено в схеме,
    чтобы не тянуть отдельную миграцию только ради него."""

    connection_id = fields.CharField(max_length=255, pk=True)
    enabled = fields.BooleanField(default=True)
    last_post_date = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "story_autopost"


async def is_autopost_enabled(connection_id):
    rows = await StoryAutopost.filter(connection_id=connection_id).values("enabled")
    return bool(rows and rows[0]["enabled"])


async def toggle_autopost(connection_id):
    enabled = await is_autopost_enabled(connection_id)
    if enabled:
        await StoryAutopost.filter(connection_id=connection_id).update(enabled=False)
    else:
        await StoryAutopost.update_or_create(
            connection_id=connection_id, defaults={"enabled": True}
        )
    return not enabled
