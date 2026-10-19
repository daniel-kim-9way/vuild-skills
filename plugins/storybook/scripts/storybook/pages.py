"""확인 화면(HTML)을 만든다. 모양은 assets/templates에 있고, 여기서는 데이터만 넣는다.
인터넷에서 불러오는 것이 없다. 글꼴·css·js는 ~/동화공방/.assets에 복사해 두고 상대 경로로 쓴다
(플러그인이 업데이트돼 설치 경로가 바뀌어도 예전 화면이 깨지지 않게)."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from . import paths, story

TEMPLATES = paths.ASSETS / "templates"
FILES = {"draft": "1-글확인.html", "art": "2-그림확인.html", "book": "동화.html"}
SCREEN = {"draft": "글 확인", "art": "그림 확인", "book": "동화", "voice": "목소리 고르기"}


def install_assets() -> Path:
    target = paths.home() / ".assets"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("common.css", "common.js"):
        shutil.copyfile(TEMPLATES / name, target / name)
    font = target / "Jua-Regular.ttf"
    if not font.exists():
        shutil.copyfile(paths.ASSETS / "Jua-Regular.ttf", font)
    return target


def render(data: dict, dest: Path, assets: str) -> Path:
    install_assets()
    template = (TEMPLATES / "page.html").read_text(encoding="utf-8")
    # 글에 </script>나 <!--<script>가 있어도 데이터 칸이 깨지지 않게 < 를 \u003c로 바꾼다 (JSON에서는 같은 뜻이다)
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    dest.write_text(template.replace("__ASSETS__", assets).replace("__DATA__", payload), encoding="utf-8")
    return dest


def _versioned(folder: Path, rel: str | None) -> str | None:
    """그림을 다시 그리면 브라우저가 옛 그림을 보여 주지 않게 ?v=고친시각을 붙인다"""
    if not rel or not (folder / rel).exists():
        return None
    return f"{rel}?v={int((folder / rel).stat().st_mtime)}"


def story_data(kind: str, folder: Path) -> dict:
    folder = Path(folder)
    data = story.load(folder)
    video = story.video_path(folder, data)
    return {
        "kind": kind, "screen": SCREEN[kind], "folder": str(folder), "title": data["title"],
        "lesson": data.get("lesson", ""), "questions": data.get("questions", []),
        "cast": [{"name": c["name"], "kind": c.get("kind_ko", ""), "photo": c.get("photo")} for c in data["cast"]],
        "pages": [{"n": p["n"], "label": story.label(p["n"]), "text": p["text"],
                   "image": _versioned(folder, p["image"]), "note": p.get("redraw_note", "")} for p in data["pages"]],
        "video": video.name if video.exists() else None,
    }


def build(kind: str, folder: Path) -> Path:
    return render(story_data(kind, folder), Path(folder) / FILES[kind], "../../.assets")


def voice_page(voices: list[dict]) -> Path:
    home = paths.home()
    items = [{"id": v["id"], "label": v["label"], "file": Path(os.path.relpath(v["file"], home)).as_posix()}
             for v in voices]
    return render({"kind": "voice", "screen": SCREEN["voice"], "voices": items}, home / "목소리고르기.html", ".assets")
