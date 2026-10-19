"""fal.ai FLUX.2로 그림을 그린다 (FAL_KEY). 빠르지만(한 장 10~30초) 장마다 돈이 든다.
결과를 fal 기록에 남기지 않고 바로 받는다(sync_mode). 아이 사진이 들어가서다."""
from __future__ import annotations

import base64
import json
import random
import re
import urllib.error
import urllib.request
from pathlib import Path

from . import config
from .painter import PaintError, Request, RetryablePaintError

ENDPOINT = "fal-ai/flux-2-pro/edit"
PRICE_PER_IMAGE_KRW = (80, 130)  # 2026-10 기준 대략
TIMEOUT = 300


def estimate(count: int) -> str:
    low, high = PRICE_PER_IMAGE_KRW
    return f"{count}장, {count * low:,}~{count * high:,}원쯤"


def data_uri(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode()


class FalEngine:
    name = "fal"
    workers = 3

    def __init__(self, key: str | None = None, endpoint: str | None = None, opener=urllib.request.urlopen):
        self.key = key if key is not None else config.secret("FAL_KEY")
        if not self.key:
            raise PaintError("FAL_KEY가 없어요. sb.py env open으로 ~/동화공방/.env에 넣어 주세요")
        self.endpoint = endpoint or config.secret("FAL_IMAGE_MODEL") or ENDPOINT
        self.opener = opener

    def body(self, request: Request, attempt: int) -> dict:
        # 두 번째 시도부터 seed를 바꾼다. 같은 seed면 안전 검사에 걸린 그림이 또 같게 나온다.
        return {"prompt": request.prompt, "image_urls": [data_uri(p) for p in request.photos],
                "image_size": {"width": 1024, "height": 768}, "output_format": "jpeg",
                "safety_tolerance": "2", "sync_mode": True,
                "seed": request.seed if attempt == 1 else random.randint(1, 2_000_000_000)}

    def paint(self, request: Request, attempt: int) -> bytes:
        req = urllib.request.Request(f"https://fal.run/{self.endpoint}", method="POST",
                                     data=json.dumps(self.body(request, attempt)).encode(),
                                     headers={"Authorization": f"Key {self.key}", "Content-Type": "application/json"})
        try:
            with self.opener(req, timeout=TIMEOUT) as response:
                result = json.loads(response.read())
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode("utf-8", "replace")
            # 잔액이 떨어져도 403(«User is locked. Reason: Exhausted balance»)이 와서 잔액을 먼저 본다
            if e.code == 402 or re.search(r"balance|exhausted|credit", detail, re.I):
                raise PaintError("fal.ai 잔액이 모자라요. 충전한 뒤 «이어서 그려 줘»라고 해 주세요") from e
            if e.code in (401, 403):
                raise PaintError("fal.ai 키가 맞지 않아요. ~/동화공방/.env의 FAL_KEY를 확인해 주세요") from e
            if e.code == 429 or e.code >= 500:
                raise RetryablePaintError(f"fal.ai가 바빠요 ({e.code})") from e
            raise PaintError(f"fal.ai 오류 {e.code}: {detail[:120]}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise RetryablePaintError(f"fal.ai에 연결하지 못했어요 ({e.__class__.__name__})") from e
        except ValueError as e:
            raise RetryablePaintError("fal.ai 답을 읽지 못했어요") from e
        if any(result.get("has_nsfw_concepts") or []):
            raise RetryablePaintError("그림이 안전 검사에 걸렸어요")
        url = ((result.get("images") or [{}])[0] or {}).get("url")
        if not url:
            raise RetryablePaintError("그림이 오지 않았어요")
        if url.startswith("data:"):
            return base64.b64decode(url.split(",", 1)[1])
        try:
            with self.opener(url, timeout=TIMEOUT) as response:
                return response.read()
        except (urllib.error.URLError, OSError) as e:
            raise RetryablePaintError("그림을 내려받지 못했어요") from e

    def close(self) -> None:
        pass
