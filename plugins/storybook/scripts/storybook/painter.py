"""쪽마다 그림을 그린다. 엔진(codex.py, fal.py)은 그림 한 장 그리는 일만 하고,
순서·다시 시도·저장은 여기서 한다. 표지를 먼저 그리고, 다음 장부터는 표지를 화풍 참고로 같이 넣는다."""
from __future__ import annotations

import io
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from PIL import Image

from . import story

STYLE = ("A page from a warm children's picture book. Soft watercolor and colored-pencil illustration, "
         "gentle pastel colors, rounded friendly shapes, cozy storybook lighting, simple clean background details.")
RULES = ("Draw the child as an illustrated storybook character who clearly looks like the child in the reference photo "
         "(same face shape, hairstyle, hair color and skin tone), not as a photograph. "
         "Draw each toy as a living storybook character that keeps the exact colors, patterns and shape of its reference photo. "
         "Keep every character consistent with its reference. No text, no letters, no speech bubbles, no watermark.")
COVER_NOTE = "This is the front cover illustration, leave calm empty space at the top."
ATTEMPTS = 3
LOCK_NAME = ".drawing"  # 동화 폴더에 두는 «그리는 중» 표시
LOCK_STALE = 15 * 60    # 한 번 시도는 10분 안에 끝나니, 이보다 오래 안 바뀐 표시는 꺼진 draw가 남긴 것이다


class PaintError(Exception):
    """사람에게 물어야 하는 실패 (사용량 한도, 키 오류, 잔액 부족)"""


class RetryablePaintError(PaintError):
    """다시 그려 볼 만한 실패 (시간 초과, 안전 검사, 서버 오류)"""


@dataclass
class Request:
    n: int
    prompt: str
    keys: list            # 참고 사진 순서가 곧 image 1, image 2 …
    photos: list          # keys와 같은 순서의 사진 경로
    style: Optional[Path]  # 표지 그림 (본문 쪽에만)
    seed: int


def role_en(key: str) -> str:
    return "the child" if key == "child" else "the toy friend"


def request_for(data: dict, page: dict, folder: Path) -> Request:
    """그림 지시문과 참고 사진 목록을 만든다. [child]·[toy1] 표시는 «image N의 누구»로 바꾼다."""
    by_key = {member["key"]: member for member in data["cast"]}
    keys = [key for key in page["cast"] if key in by_key] or ["child"]
    scene = page["prompt_en"]
    for i, key in enumerate(keys, 1):
        scene = scene.replace(f"[{key}]", f"{role_en(key)} from image {i}")
    scene = story.MARKER.sub("a friend", scene)
    references = []
    for i, key in enumerate(keys, 1):
        default = "the main child of the story" if key == "child" else "the child's favorite toy"
        references.append(f"Image {i} is the reference photo of {role_en(key)}: {by_key[key].get('look_en') or default}.")
    parts = [STYLE, COVER_NOTE if page["n"] == 0 else None, scene, " ".join(references), RULES]
    cover = Path(folder) / "그림" / image_name(0)
    return Request(n=page["n"], prompt="\n".join(p for p in parts if p), keys=keys,
                   photos=[Path(folder) / by_key[key]["photo"] for key in keys],
                   style=cover if page["n"] > 0 and cover.exists() else None, seed=int(data.get("seed") or 1))


def to_jpeg(raw: bytes) -> bytes:
    """화면 그림 칸(4:3)에 맞게 가운데를 잘라 JPG로 만든다"""
    with Image.open(io.BytesIO(raw)) as opened:
        image = opened.convert("RGBA") if opened.mode in ("RGBA", "LA", "P") else opened.convert("RGB")
    if image.mode == "RGBA":
        flat = Image.new("RGB", image.size, (255, 255, 255))
        flat.paste(image, mask=image.getchannel("A"))
        image = flat
    width = min(image.width, round(image.height * 4 / 3))
    if width < image.width:
        left = (image.width - width) // 2
        image = image.crop((left, 0, left + width, image.height))
    out = io.BytesIO()
    image.save(out, "JPEG", quality=88)
    return out.getvalue()


def image_name(n: int) -> str:
    return "cover.jpg" if n == 0 else f"p{n}.jpg"


def pending(data: dict, only: list[int] | None = None, folder: Path | None = None) -> list[dict]:
    """아직 그림이 없는 쪽 (only가 있으면 그 쪽들만). folder를 주면 그림 파일이 없어진 쪽도 넣는다."""
    def missing(page: dict) -> bool:
        return page["image"] is None or (folder is not None and not (Path(folder) / page["image"]).exists())
    return [p for p in data["pages"] if missing(p) and (only is None or p["n"] in only)]


BUSY = "이 동화는 지금 그리는 중이에요. 다 그렸다는 말이 나온 뒤에 다시 해 주세요"


def _stale(lock: Path) -> bool:
    """«그리는 중» 표시가 꺼진 draw가 남긴 것인지. 오래됐거나, 적힌 프로세스가 없으면 그렇다."""
    try:
        if time.time() - lock.stat().st_mtime >= LOCK_STALE:
            return True
        pid = int(lock.read_text(encoding="utf-8").strip() or 0)
    except (OSError, ValueError):
        return True
    if os.name != "nt" and pid > 0:  # 윈도우의 os.kill은 그 프로세스를 꺼 버려서 쓰지 않는다
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
    return False


def drawing(folder: Path) -> bool:
    """지금 이 동화를 그리는 중인지"""
    lock = Path(folder) / LOCK_NAME
    return lock.exists() and not _stale(lock)


def _take_lock(folder: Path) -> Path:
    """같은 동화를 두 군데서 같이 그리지 않게 표시를 남긴다. 표시는 한 번에 하나만 만들어진다(O_EXCL)."""
    lock = folder / LOCK_NAME
    for _ in range(2):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if not _stale(lock):
                raise PaintError(BUSY) from None
            lock.unlink(missing_ok=True)
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(str(os.getpid()))
        return lock
    raise PaintError(BUSY)


def _as_object(n: int) -> str:
    return "표지를" if n == 0 else f"{n}쪽을"


def draw(folder: Path, engine, only: list[int] | None = None,
         progress: Callable[[str], None] = print) -> list[int]:
    """그림이 없는 쪽을 그리고, 그린 쪽 번호를 돌려준다.
    PaintError가 나면 그때까지 그린 것은 story.json에 남기고 그대로 올려 보낸다. 다시 부르면 남은 쪽만 그린다.
    그리는 동안 다른 데서 story.json을 고칠 수 있어서, 한 장마다 새로 읽어 그 쪽 그림만 넣는다."""
    folder = Path(folder)
    (folder / "그림").mkdir(exist_ok=True)
    marker: Path | None = None
    data = story.load(folder)
    todo = pending(data, only, folder)
    total = len(todo)
    done: list[int] = []
    lock = threading.Lock()

    def one(page: dict) -> None:
        with lock:  # 차례를 기다리는 동안 지시문을 고쳤을 수 있어서 새로 읽는다
            fresh = story.load(folder)
        page = next(p for p in fresh["pages"] if p["n"] == page["n"])
        request = request_for(fresh, page, folder)
        raw = b""
        for attempt in range(1, ATTEMPTS + 1):
            if marker is not None:
                marker.touch()
            try:
                raw = engine.paint(request, attempt)
                break
            except RetryablePaintError as e:
                if attempt == ATTEMPTS:
                    raise PaintError(f"{_as_object(page['n'])} {ATTEMPTS}번 그려 봤는데 안 됐어요: {e}") from e
                progress(f"  {story.label(page['n'])} 다시 그려요 ({e})")
        name = image_name(page["n"])
        picture = to_jpeg(raw)
        with lock:
            fresh = story.load(folder)
            now = next(p for p in fresh["pages"] if p["n"] == page["n"])
            if (now["prompt_en"], now["cast"]) != (page["prompt_en"], page["cast"]):
                progress(f"{story.label(page['n'])}: 그리는 동안 지시문이 바뀌어서 다음에 다시 그려요")
                return
            (folder / "그림" / name).write_bytes(picture)
            now["image"] = f"그림/{name}"
            now["zones"] = []
            story.save(folder, fresh)
            done.append(page["n"])
            progress(f"그림 {len(done)}/{total}: {story.label(page['n'])}")

    try:
        marker = _take_lock(folder)
        for page in [p for p in todo if p["n"] == 0]:
            one(page)
        rest = [p for p in todo if p["n"] != 0]
        if engine.workers <= 1:
            for page in rest:
                one(page)
        else:
            pool = ThreadPoolExecutor(engine.workers)
            try:
                for future in [pool.submit(one, page) for page in rest]:
                    future.result()
            finally:  # 멈추면 줄 서 있던 쪽은 그리지 않는다 (fal이면 돈이 나가지 않게)
                pool.shutdown(wait=True, cancel_futures=True)
    finally:
        engine.close()
        if marker is not None:
            marker.unlink(missing_ok=True)
    return sorted(done)
