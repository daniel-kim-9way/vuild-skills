"""그림에서 덜 복잡한 곳(하늘, 바닥, 빈 벽)을 찾아 글을 얹을 자리를 고른다. 앱 TextLayout을 Pillow로 옮겼다.
문장이 바뀌면 앞 문장과 겹치지 않는 다른 자리로 옮긴다. 그림책처럼 글이 그림 위를 오가게 하려는 것이다."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter, ImageStat

# 자리 이름 => 그림 안의 칸 (왼쪽, 위, 너비, 높이를 그림 크기에 대한 비율로)
ZONES = {
    "top": (0.05, 0.04, 0.90, 0.28),
    "bottom": (0.05, 0.68, 0.90, 0.28),
    "top-left": (0.04, 0.04, 0.46, 0.38),
    "top-right": (0.50, 0.04, 0.46, 0.38),
    "bottom-left": (0.04, 0.58, 0.46, 0.38),
    "bottom-right": (0.50, 0.58, 0.46, 0.38),
}
WIDE = ("top", "bottom")
# 이 글자 수보다 긴 문장은 좁은 모서리 칸에 넣으면 줄이 너무 많아진다
CORNER_LIMIT = 20
# 그림책은 위쪽 여백에 글을 많이 둔다. 위쪽 칸을 조금 더 좋아한다.
TOP_BONUS = 0.85
# 옮겨 갈 자리가 이만큼 더 복잡하면 옮기지 않는다
CALM = 10


def fallback(count: int) -> list[str]:
    """그림을 못 읽으면 위·아래를 번갈아 쓴다"""
    return ["top" if i % 2 == 0 else "bottom" for i in range(count)]


def busyness(image_path: Path) -> dict[str, float]:
    """칸마다 선(윤곽)이 얼마나 많은지 잰다. 적을수록 글을 얹기 좋다."""
    with Image.open(image_path) as opened:
        small = opened.convert("L")
    small.thumbnail((320, 100_000))
    edges = small.filter(ImageFilter.FIND_EDGES)
    width, height = edges.size
    scores = {}
    for name, (x, y, w, h) in ZONES.items():
        box = (round(x * width), round(y * height), round((x + w) * width), round((y + h) * height))
        score = ImageStat.Stat(edges.crop(box)).mean[0]
        scores[name] = score * TOP_BONUS if name.startswith("top") else score
    return scores


def overlap(a: str, b: str) -> bool:
    if a == b:
        return True

    def vertical(zone):
        return "top" if zone.startswith("top") else "bottom"

    def side(zone):
        return "left" if zone.endswith("left") else "right" if zone.endswith("right") else "both"

    if vertical(a) != vertical(b):
        return False
    return "both" in (side(a), side(b)) or side(a) == side(b)


def zones(image_path: Path, chunks: list[str], cover: bool = False) -> list[str]:
    try:
        busy = busyness(image_path)
    except (OSError, ValueError):
        return fallback(len(chunks))
    picks: list[str] = []
    for chunk in chunks:
        allowed = list(WIDE) if cover or len(chunk) > CORNER_LIMIT else list(ZONES)
        ranked = sorted(allowed, key=lambda zone: busy[zone])
        previous = picks[-1] if picks else None
        choice = next((z for z in ranked if previous is None or not overlap(z, previous)), ranked[0])
        # 옮겨 갈 자리가 그림 한가운데처럼 너무 복잡하면 같은 자리를 한 번 더 쓴다
        if busy[choice] > busy[ranked[0]] * 2.2 + CALM:
            choice = ranked[0]
        picks.append(choice)
    return picks
