from tortoise import fields
from tortoise.models import Model


class UserLocale(Model):
    owner_id = fields.BigIntField(pk=True, generated=False)
    locale = fields.CharField(max_length=8, default="ru")

    class Meta:
        table = "user_locale"
