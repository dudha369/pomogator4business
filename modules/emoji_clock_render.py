import io

from PIL import Image, ImageDraw, ImageFont

_FONT_PATH = "assets/fonts/Baloo2-Bold.ttf"
_CANVAS_SIZE = 100
_SUPERSAMPLE = 4
_BOLD_WEIGHT = 800

_BADGE_MARGIN_X = 7
_BADGE_MARGIN_Y = 31
_CORNER_RADIUS = 10
_STROKE_WIDTH = 3
_TEXT_PADDING_X = 6


def _load_font(size):
    font = ImageFont.truetype(_FONT_PATH, size)
    try:
        font.set_variation_by_axes([_BOLD_WEIGHT])
    except Exception:
        pass
    return font


def render_clock_emoji(time_text):
    scale = _SUPERSAMPLE
    big_size = _CANVAS_SIZE * scale

    canvas = Image.new("RGBA", (big_size, big_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    margin_x = _BADGE_MARGIN_X * scale
    margin_y = _BADGE_MARGIN_Y * scale
    radius = _CORNER_RADIUS * scale
    stroke_width = _STROKE_WIDTH * scale

    badge_box = [margin_x, margin_y, big_size - margin_x, big_size - margin_y]
    draw.rounded_rectangle(
        badge_box,
        radius=radius,
        outline=(0, 0, 0, 255),
        width=stroke_width,
    )

    badge_width = badge_box[2] - badge_box[0]
    badge_height = badge_box[3] - badge_box[1]
    max_text_width = badge_width - (_TEXT_PADDING_X * scale + stroke_width) * 2
    max_text_height = badge_height - stroke_width * 3

    font_size = int(badge_height * 0.6)
    font = _load_font(font_size)
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    while (text_w > max_text_width or text_h > max_text_height) and font_size > 8:
        font_size -= 1
        font = _load_font(font_size)
        bbox = draw.textbbox((0, 0), time_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

    x = (big_size - text_w) / 2 - bbox[0]
    y = (big_size - text_h) / 2 - bbox[1]
    draw.text((x, y), time_text, font=font, fill=(0, 0, 0, 255))

    return canvas.resize((_CANVAS_SIZE, _CANVAS_SIZE), Image.LANCZOS)


def render_to_bytes(time_text):
    canvas = render_clock_emoji(time_text)
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()
