from tortoise import fields
from tortoise.models import Model


class StoryAutopost(Model):
    connection_id = fields.CharField(max_length=255, pk=True)
    enabled = fields.BooleanField(default=True)
    last_post_date = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "story_autopost"


class StoryQueue(Model):
    queue_id = fields.BigIntField(pk=True)
    connection_id = fields.CharField(max_length=255)
    tile_data = fields.BinaryField()

    class Meta:
        table = "story_queue"
