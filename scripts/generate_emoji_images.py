import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.emoji_clock_render import render_clock_emoji

OUTPUT_DIR = "assets/generated_emoji"
PACK_SIZE = 180
PACK_COUNT = 8


def all_time_keys():
    return [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)]


def main():
    times = all_time_keys()
    assert len(times) == PACK_SIZE * PACK_COUNT

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for pack_index in range(PACK_COUNT):
        pack_dir = os.path.join(OUTPUT_DIR, f"pack_{pack_index}")
        os.makedirs(pack_dir, exist_ok=True)

        chunk = times[pack_index * PACK_SIZE : (pack_index + 1) * PACK_SIZE]
        for time_key in chunk:
            image = render_clock_emoji(time_key)
            safe_name = time_key.replace(":", "-")
            image.save(os.path.join(pack_dir, f"{safe_name}.png"))

        print(f"pack_{pack_index}: {len(chunk)} изображений сохранено в {pack_dir}")

    print(f"Готово: {len(times)} изображений в {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
