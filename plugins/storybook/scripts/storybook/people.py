"""아이·인형 사진을 정리하고, 한 번 올린 인물을 저장해 두었다가 다시 쓴다.

~/동화공방/인물/<이름>/photo.jpg, info.json
"""
from __future__ import annotations

import shutil
import warnings
from pathlib import Path

from PIL import Image, ImageOps

from . import config, paths

try:  # 아이폰 HEIC 사진도 읽는다
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:  # pragma: no cover
    pass

MAX_SIDE = 1000
# Pillow는 약 1억 8천만 화소가 넘으면 압축 폭탄으로 보고 멈춘다. 2억 화소 휴대폰 사진은 받고, 그보다 훨씬 크면 거절한다.
PIXEL_LIMIT = 250_000_000
ROLES = ("child", "toy")


class PersonError(Exception):
    pass


def clean_photo(src: Path, dest: Path) -> Path:
    """긴 변 1000px JPG로 다시 저장한다. 똑바로 세우고, 촬영 위치(GPS)·기기 정보(EXIF)는 남기지 않는다."""
    default_limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = PIXEL_LIMIT // 2  # Pillow는 이 값의 두 배에서 멈춘다
    try:
        with warnings.catch_warnings():
            # 한도의 절반이 넘으면 Pillow가 영어 경고를 찍는다. 2억 화소 휴대폰 사진도 여기 들어가서 끈다.
            warnings.simplefilter("ignore", Image.DecompressionBombWarning)
            with Image.open(src) as opened:
                opened.draft(None, (MAX_SIDE, MAX_SIDE))  # JPG는 줄여서 읽어 메모리를 아낀다
                image = ImageOps.exif_transpose(opened)
                image.load()
    except Image.DecompressionBombError as e:
        raise PersonError(f"사진이 너무 커요: {Path(src).name} (2억 화소보다 큰 사진은 줄여서 올려 주세요)") from e
    except (OSError, ValueError) as e:
        raise PersonError(f"사진을 읽지 못했어요: {Path(src).name}") from e
    finally:
        Image.MAX_IMAGE_PIXELS = default_limit
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        image = Image.new("RGB", rgba.size, (255, 255, 255))
        image.paste(rgba, mask=rgba.getchannel("A"))
    image = image.convert("RGB")
    image.thumbnail((MAX_SIDE, MAX_SIDE))
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest, "JPEG", quality=88)  # exif를 넘기지 않으니 정보가 남지 않는다
    return dest


def _folder(name: str) -> Path:
    return paths.people_dir() / paths.safe_name(name, 30)


def save_person(name: str, role: str, photo: Path, age: int | None = None) -> dict:
    """인물을 저장한다. 같은 이름이 있으면 새 사진과 역할로 바꾸고, 예전 생김새 설명은 지운다."""
    name = str(name).strip()
    if not name:
        raise PersonError("이름이 비어 있어요")
    if role not in ROLES:
        raise PersonError(f"역할은 child(아이) 또는 toy(인형)예요: {role}")
    folder = _folder(name)
    clean_photo(Path(photo), folder / "photo.jpg")
    info = {"name": name, "role": role, "age": age if role == "child" else None,
            "kind_ko": "아이" if role == "child" else "", "look_en": ""}
    config.write_json(folder / "info.json", info)
    return {**info, "photo": str(folder / "photo.jpg")}


def list_people() -> list[dict]:
    root = paths.people_dir()
    if not root.is_dir():
        return []
    found = []
    for folder in sorted(root.iterdir()):
        info_file, photo = folder / "info.json", folder / "photo.jpg"
        if folder.is_dir() and info_file.exists() and photo.exists():
            found.append({**config.read_json(info_file), "photo": str(photo)})
    return found


def get_person(name: str) -> dict:
    for person in list_people():
        if person["name"] == str(name).strip():
            return person
    raise PersonError(f"저장한 인물 중에 «{name}»이(가) 없어요")


def remove_person(name: str) -> None:
    person = get_person(name)
    shutil.rmtree(Path(person["photo"]).parent)


def remember_looks(cast: list[dict]) -> None:
    """동화를 쓰며 적은 생김새 설명(look_en)과 인형 종류(kind_ko)를 저장한 인물에도 남긴다."""
    for member in cast:
        info_file = _folder(member.get("name", "")) / "info.json"
        if not info_file.exists():
            continue
        info = config.read_json(info_file)
        if member.get("look_en"):
            info["look_en"] = member["look_en"]
        if member.get("kind_ko") and info.get("role") == "toy":
            info["kind_ko"] = member["kind_ko"]
        config.write_json(info_file, info)
