"""동화 폴더(~/동화공방/동화/<날짜>-<제목>/)와 그 안의 story.json을 다룬다. 모양은 reference/story-format.md에 있다.
story.json은 이 모듈을 거쳐서 고친다. 그래야 글을 고쳤을 때 옛 목소리가, 지시문을 고쳤을 때 옛 그림이 남지 않는다."""
from __future__ import annotations

import datetime
import random
import re
import shutil
from pathlib import Path

import yaml

from . import chunks, config, paths, people

PAGES = 9  # 표지 1 + 본문 8
TOY_KEYS = ("toy1", "toy2", "toy3")
MUSIC = ("lullaby", "twinkle", "meadow", "off")
MARKER = re.compile(r"\[(child|toy\d)\]")
HANGUL = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")


class StoryError(Exception):
    def __init__(self, problems: list[str]):
        super().__init__("\n".join(problems))
        self.problems = problems


def label(n: int) -> str:
    return "표지" if n == 0 else f"{n}쪽"


def normalize(draft: dict) -> dict:
    """Claude가 쓴 초안을 story.json 모양으로 바꾼다. 그림·목소리 칸은 비워 둔다."""
    title = str(draft.get("title", "")).strip()
    pages = []
    for n, page in enumerate(draft.get("pages") or []):
        pages.append({"n": n, "text": str(page.get("text", "")).strip(),
                      "cast": [str(key) for key in page.get("cast") or []],
                      "prompt_en": str(page.get("prompt_en", "")).strip(),
                      "image": None, "redraw_note": "", "voices": [], "zones": []})
    if pages:
        pages[0]["text"] = title
    cast = []
    for member in draft.get("cast") or []:
        child = member.get("key") == "child"
        cast.append({"key": str(member.get("key", "")), "name": str(member.get("name", "")).strip(),
                     "age": member.get("age") if child else None,
                     "kind_ko": str(member.get("kind_ko") or ("아이" if child else "")).strip(),
                     "look_en": str(member.get("look_en", "")).strip(), "photo": ""})
    questions = [str(q).strip() for q in draft.get("questions") or [] if str(q).strip()]
    return {"version": 1, "title": title, "lesson": str(draft.get("lesson", "")).strip(),
            "theme": str(draft.get("theme", "")).strip(), "wish": str(draft.get("wish", "")).strip(),
            "music": draft.get("music") or "lullaby", "created": "", "seed": random.randint(1, 2_000_000_000),
            "cast": cast, "questions": questions[:3], "pages": pages}


def check(data: dict) -> tuple[list[str], list[str]]:
    """(고쳐야 하는 것, 한 번 더 볼 것)"""
    errors: list[str] = []
    warnings: list[str] = []
    if not data.get("title"):
        errors.append("제목이 비어 있어요")
    keys = [c["key"] for c in data.get("cast", [])]
    if keys[:1] != ["child"] or keys.count("child") != 1:
        errors.append("cast 맨 앞에 아이(child)가 한 명 있어야 해요")
    toys = keys[1:]
    if not 1 <= len(toys) <= 3 or len(set(toys)) != len(toys) or any(k not in TOY_KEYS for k in toys):
        errors.append("인형은 toy1~toy3으로 1~3개여야 해요")
    for member in data.get("cast", []):
        if not member.get("name"):
            errors.append(f"{member.get('key')}의 이름이 비어 있어요")
        if not member.get("look_en"):
            errors.append(f"{member.get('name') or member.get('key')}의 생김새 설명(look_en)이 비어 있어요")
    if data.get("music") not in MUSIC:
        errors.append(f"음악은 {', '.join(MUSIC)} 중 하나예요")
    pages = data.get("pages", [])
    if len(pages) != PAGES:
        errors.append(f"표지 1쪽과 본문 8쪽, 모두 9쪽이어야 해요 (지금 {len(pages)}쪽)")
    names = [c["name"] for c in data.get("cast", []) if c.get("name")]
    for page in pages:
        where = label(page["n"])
        if not page["text"]:
            errors.append(f"{where} 글이 비어 있어요")
        if not page["cast"]:
            errors.append(f"{where}에 나오는 인물(cast)이 없어요")
        unknown = [k for k in page["cast"] if k not in keys]
        if unknown:
            errors.append(f"{where} cast에 없는 인물이 있어요: {', '.join(unknown)}")
        prompt = page["prompt_en"]
        if not prompt:
            errors.append(f"{where} 그림 지시문(prompt_en)이 비어 있어요")
        elif HANGUL.search(prompt):
            errors.append(f"{where} 그림 지시문은 영어로만 써요 (이름은 [child]·[toy1] 표시로)")
        elif any(name in prompt for name in names):
            errors.append(f"{where} 그림 지시문에 이름 대신 [child]·[toy1] 표시를 써요")
        stray = [k for k in MARKER.findall(prompt) if k not in page["cast"]]
        if stray:
            warnings.append(f"{where} 지시문의 {', '.join('[' + k + ']' for k in stray)}가 cast에 없어요")
        if page["n"] > 0 and page["text"]:
            if not 40 <= len(page["text"]) <= 90:
                warnings.append(f"{where} 글이 {len(page['text'])}자예요 (40~90자가 좋아요)")
            if len(chunks.split(page["text"])) > 3:
                warnings.append(f"{where} 문장이 많아요 (1~3문장이 좋아요)")
    if len(data.get("questions", [])) < 2:
        warnings.append("다 읽고 물어볼 질문이 2개면 좋아요")
    return errors, warnings


def create(draft: dict, today: datetime.date | None = None) -> Path:
    """초안으로 동화 폴더를 만든다. 인물 사진은 저장한 인물에서 복사해 온다."""
    data = normalize(draft)
    errors, _ = check(data)
    sources = {}
    for member in data["cast"]:
        try:
            sources[member["key"]] = Path(people.get_person(member["name"])["photo"])
        except people.PersonError as e:
            errors.append(f"{e}. 먼저 sb.py people add로 저장해 주세요")
    if errors:
        raise StoryError(errors)
    day = today or datetime.date.today()
    data["created"] = day.isoformat()
    folder = _new_folder(data["title"], day)
    for sub in ("사진", "그림", "목소리"):
        (folder / sub).mkdir(exist_ok=True)
    for member in data["cast"]:
        shutil.copyfile(sources[member["key"]], folder / "사진" / f"{member['key']}.jpg")
        member["photo"] = f"사진/{member['key']}.jpg"
    save(folder, data)
    people.remember_looks(data["cast"])
    return folder


def _new_folder(title: str, day: datetime.date) -> Path:
    base = f"{day.isoformat()}-{paths.safe_name(title, 40).replace(' ', '-')}"
    folder = paths.stories_dir() / base
    number = 2
    while folder.exists():
        folder = paths.stories_dir() / f"{base}-{number}"
        number += 1
    folder.mkdir(parents=True)
    return folder


def load(folder: Path) -> dict:
    try:
        return config.read_json(Path(folder) / "story.json")
    except FileNotFoundError as e:
        raise StoryError([f"동화 폴더가 아니에요 (story.json이 없어요): {folder}"]) from e


def save(folder: Path, data: dict) -> None:
    config.write_json(Path(folder) / "story.json", data)


def page_of(data: dict, n: int) -> dict:
    for page in data["pages"]:
        if page["n"] == n:
            return page
    raise StoryError([f"{n}쪽은 없어요 (0은 표지, 1~8은 본문)"])


def edit(folder: Path, n: int, *, text: str | None = None, prompt_en: str | None = None,
         cast: list[str] | None = None, redraw: bool = False, note: str = "") -> dict:
    """한 쪽을 고친다. 글이 바뀌면 목소리·글 자리를 비우고, 지시문·인물이 바뀌거나 redraw면 그림을 지운다."""
    data = load(folder)
    page = page_of(data, n)
    if text is not None and text.strip() != page["text"]:
        page["text"] = text.strip()
        page["voices"] = []
        page["zones"] = []
        if n == 0:
            data["title"] = page["text"]
    if prompt_en is not None and prompt_en.strip() != page["prompt_en"]:
        page["prompt_en"] = prompt_en.strip()
        redraw = True
    if cast is not None and list(cast) != page["cast"]:
        page["cast"] = list(cast)
        redraw = True
    errors, _ = check(data)
    if errors:
        raise StoryError(errors)
    if redraw:
        if page["image"]:
            (Path(folder) / page["image"]).unlink(missing_ok=True)
        page["image"] = None
        page["zones"] = []
        page["redraw_note"] = note.strip()
    save(folder, data)
    return page


def delete(folder: Path) -> None:
    """동화 폴더 하나를 지운다. 동화 폴더가 아니면 손대지 않는다."""
    folder = Path(folder).resolve()
    if folder.parent != paths.stories_dir().resolve() or not (folder / "story.json").exists():
        raise StoryError([f"동화 폴더만 지울 수 있어요: {folder}"])
    shutil.rmtree(folder)


def all_stories() -> list[Path]:
    """최근 것부터"""
    root = paths.stories_dir()
    if not root.is_dir():
        return []
    return sorted((p for p in root.iterdir() if (p / "story.json").exists()), key=lambda p: p.name, reverse=True)


def video_path(folder: Path, data: dict) -> Path:
    return Path(folder) / f"{paths.safe_name(data['title'])}.mp4"


def summary(folder: Path) -> str:
    data = load(folder)
    drawn = sum(1 for p in data["pages"] if p["image"])
    video = "MP4 있음" if video_path(folder, data).exists() else "MP4 없음"
    return f"{folder}\t{data['title']}\t그림 {drawn}/{len(data['pages'])}\t{video}"


def _patterns() -> dict:
    return yaml.safe_load((paths.REFERENCE / "patterns.yml").read_text(encoding="utf-8"))


def themes() -> list[dict]:
    return _patterns()["themes"]


def examples(theme: str) -> str:
    """그 주제의 예시 동화를 글로 꺼낸다. Claude가 흐름과 교훈만 참고한다."""
    data = _patterns()
    info = next((t for t in data["themes"] if t["key"] == theme), None)
    if info is None:
        keys = ", ".join(t["key"] for t in data["themes"])
        raise StoryError([f"없는 주제예요: {theme} (고를 수 있는 것: {keys})"])
    blocks = [f"주제: {info['label']} ({info['desc']})"]
    for pattern in data["patterns"]:
        if pattern["theme"] != theme:
            continue
        lines = [f'<예시 제목="{pattern["title"]}" 교훈="{pattern["lesson"]}">']
        lines += [f"{i}쪽: {page['text']}" for i, page in enumerate(pattern["pages"], 1)]
        lines.append("</예시>")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
