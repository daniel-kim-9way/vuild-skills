"""그림 9장을 3×3 한 장으로 모은다. Claude가 한눈에 보고 확인하는 데 쓴다."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import paths, story

TILE_WIDTH, TILE_HEIGHT, PAD, COLUMNS = 480, 360, 6, 3
OUTLINE = (58, 36, 22)


def build(folder: Path) -> Path:
    folder = Path(folder)
    pages = story.load(folder)["pages"]
    rows = (len(pages) + COLUMNS - 1) // COLUMNS
    canvas = Image.new("RGB", (COLUMNS * TILE_WIDTH + (COLUMNS + 1) * PAD, rows * TILE_HEIGHT + (rows + 1) * PAD), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(paths.ASSETS / "Jua-Regular.ttf"), 30)
    for i, page in enumerate(pages):
        x = PAD + (i % COLUMNS) * (TILE_WIDTH + PAD)
        y = PAD + (i // COLUMNS) * (TILE_HEIGHT + PAD)
        image_path = folder / page["image"] if page["image"] else None
        if image_path and image_path.exists():
            with Image.open(image_path) as opened:
                canvas.paste(ImageOps.fit(opened.convert("RGB"), (TILE_WIDTH, TILE_HEIGHT)), (x, y))
        else:
            draw.rectangle([x, y, x + TILE_WIDTH - 1, y + TILE_HEIGHT - 1], fill=(235, 235, 235))
        draw.text((x + 12, y + 8), story.label(page["n"]), font=font, fill="white", stroke_width=4, stroke_fill=OUTLINE)
    out = folder / "그림" / "_모아보기.jpg"
    canvas.save(out, "JPEG", quality=85)
    return out
