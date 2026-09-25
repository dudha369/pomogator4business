import asyncio
import io

from PIL import Image
from aiogram.types import (
    BufferedInputFile,
    InputMediaPhoto,
    InputStoryContentPhoto,
)

from core.context import CommandContext
from core.registry import command
from core import database as db

_GRID = {
    3: (3, 1),
    6: (3, 2),
    9: (3, 3),
}
_ACTIVE_PERIOD = 86400
_POST_DELAY = 1.0

# Ровно то, что требует Telegram для Историй (1080x1920, 9:16). Каждый тайл
# должен сам по себе быть именно такого размера — иначе при просмотре
# мозаика "поплывёт", даже если исходное фото было разрезано ровно.
_TILE_W = 1080
_TILE_H = 1920


def _cover_crop(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Растягивает/обрезает image так, чтобы он ЗАПОЛНИЛ target_w x target_h
    без искажения пропорций (аналог CSS object-fit: cover) — лишнее по
    краям обрезается, а не остаётся полосами."""
    src_w, src_h = image.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        new_h = target_h
        new_w = round(src_w * (target_h / src_h))
    else:
        new_w = target_w
        new_h = round(src_h * (target_w / src_w))

    resized = image.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def split_image(image_bytes, parts):
    """Режет фото на сетку тайлов размером ровно _TILE_W x _TILE_H каждый.

    Сначала всё исходное фото приводится (обрезкой, не растяжением) к
    размеру ВСЕЙ сетки целиком (cols*_TILE_W x rows*_TILE_H), и только
    потом эта единая картинка режется на решётку — так каждый отдельный
    тайл получается точно нужных Telegram пропорций 9:16, а не пропорций
    исходного фото.
    """
    rows, cols = _GRID[parts]
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    canvas = _cover_crop(image, _TILE_W * cols, _TILE_H * rows)

    tiles = []
    for row in range(rows):
        for col in range(cols):
            box = (
                col * _TILE_W,
                row * _TILE_H,
                (col + 1) * _TILE_W,
                (row + 1) * _TILE_H,
            )
            tile = canvas.crop(box)
            buffer = io.BytesIO()
            tile.save(buffer, format="JPEG", quality=95)
            tiles.append(buffer.getvalue())
    return tiles


async def _post_tile(bot, connection_id, tile_bytes):
    content = InputStoryContentPhoto.model_construct(
        photo=BufferedInputFile(tile_bytes, filename="story.jpg")
    )
    await bot.post_story(
        business_connection_id=connection_id,
        content=content,
        active_period=_ACTIVE_PERIOD,
    )


async def _post_all(bot, connection_id, tiles):
    for tile_bytes in tiles:
        try:
            await _post_tile(bot, connection_id, tile_bytes)
        except Exception:
            pass
        await asyncio.sleep(_POST_DELAY)


def _parts_from_args(raw_args: str) -> int:
    raw_parts = raw_args.strip()
    return int(raw_parts) if raw_parts.isdigit() and int(raw_parts) in _GRID else 9


async def _get_target_tiles(ctx: CommandContext):
    """Общая часть /story и /storysplit: найти фото в реплае и разрезать."""
    target = ctx.message.reply_to_message
    if not target or not target.photo:
        await ctx.usage_error(ctx.t("story.usage_reply"))
        return None

    parts = _parts_from_args(ctx.args)
    photo = target.photo[-1]
    file = await ctx.bot.get_file(photo.file_id)
    buffer = await ctx.bot.download_file(file.file_path)
    return split_image(buffer.read(), parts), parts


@command(
    name="story", module="story", description="Разрезает фото и публикует как Истории"
)
async def cmd_story(ctx: CommandContext):
    result = await _get_target_tiles(ctx)
    if result is None:
        return
    tiles, parts = result

    await ctx.delete_command_message()

    if await db.is_autopost_enabled(ctx.connection_id):
        await db.queue_story_tiles(ctx.connection_id, tiles)
        await ctx.edit_command_message(ctx.t("story.queued", parts=parts))
        return

    await _post_all(ctx.bot, ctx.connection_id, tiles)
    await ctx.edit_command_message(ctx.t("story.published", parts=parts))


@command(
    name="storysplit",
    module="story",
    description="Просто разрезает фото на части — без публикации в Истории",
)
async def cmd_storysplit(ctx: CommandContext):
    result = await _get_target_tiles(ctx)
    if result is None:
        return
    tiles, _parts = result

    await ctx.delete_command_message()

    media = [
        InputMediaPhoto(media=BufferedInputFile(tile, filename=f"tile_{i + 1}.jpg"))
        for i, tile in enumerate(tiles)
    ]
    try:
        await ctx.bot.send_media_group(
            business_connection_id=ctx.connection_id,
            chat_id=ctx.chat_id,
            media=media,
        )
    except Exception:
        pass


@command(
    name="storyautopost",
    module="story",
    description="Переключает публикацию по одному тайлу в день вместо сразу всех",
)
async def cmd_storyautopost(ctx: CommandContext):
    enabled = await db.toggle_autopost(ctx.connection_id)
    status = ctx.t("story.status_on") if enabled else ctx.t("story.status_off")
    await ctx.edit_command_message(ctx.t("story.autopost_toggled", status=status))


async def autopost_tick(bot, today: str):
    connections = await db.get_autopost_enabled_connections()
    for connection_id in connections:
        if await db.get_last_post_date(connection_id) == today:
            continue
        tile_bytes = await db.pop_next_tile(connection_id)
        if tile_bytes is None:
            continue
        try:
            await _post_tile(bot, connection_id, tile_bytes)
            await db.set_last_post_date(connection_id, today)
        except Exception:
            pass