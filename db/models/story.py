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


async def queue_story_tiles(connection_id, tiles):
    await StoryQueue.bulk_create(
        [StoryQueue(connection_id=connection_id, tile_data=tile) for tile in tiles]
    )


async def pop_next_tile(connection_id):
    obj = (
        await StoryQueue.filter(connection_id=connection_id)
        .order_by("queue_id")
        .first()
    )
    if not obj:
        return None
    tile_data = obj.tile_data
    await obj.delete()
    return tile_data


async def get_autopost_enabled_connections():
    return await StoryAutopost.filter(enabled=True).values_list(
        "connection_id", flat=True
    )


async def get_last_post_date(connection_id):
    rows = await StoryAutopost.filter(connection_id=connection_id).values(
        "last_post_date"
    )
    return rows[0]["last_post_date"] if rows else None


async def set_last_post_date(connection_id, date_str):
    await StoryAutopost.filter(connection_id=connection_id).update(
        last_post_date=date_str
    )
