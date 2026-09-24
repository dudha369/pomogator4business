from tortoise import fields
from tortoise.models import Model


class UserLocale(Model):
    owner_id = fields.BigIntField(pk=True, generated=False)
    locale = fields.CharField(max_length=8, default="ru")

    class Meta:
        table = "user_locale"


async def get_locale(owner_id):
    rows = await UserLocale.filter(owner_id=owner_id).values("locale")
    return rows[0]["locale"] if rows else "ru"


async def set_locale(owner_id, locale):
    await UserLocale.update_or_create(owner_id=owner_id, defaults={"locale": locale})
