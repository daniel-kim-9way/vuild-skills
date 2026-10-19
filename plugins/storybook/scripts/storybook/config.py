"""settings.json(고른 엔진)과 .env(비밀값)를 읽고 쓴다. 비밀값은 화면에 찍지 않는다."""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import paths

SECRET_NAMES = ("FAL_KEY", "FISH_AUDIO_API_KEY", "FISH_VOICE_ID")
ENV_TEMPLATE = """# 동화 공방 비밀값이에요. 이 파일은 남에게 보내지 마세요.
# 쓰는 엔진의 줄만 채우면 돼요. = 뒤에 붙여 넣고 저장하세요.
FAL_KEY=
FISH_AUDIO_API_KEY=
FISH_VOICE_ID=
"""


def settings_path() -> Path:
    return paths.home() / "settings.json"


def env_path() -> Path:
    return paths.home() / ".env"


def write_json(path: Path, data) -> None:
    """한글을 그대로 둔 JSON으로 쓴다. 반쯤 쓴 파일이 남지 않게 임시 파일에 쓰고 바꿔 끼운다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_settings() -> dict:
    try:
        return read_json(settings_path())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(**changes) -> dict:
    data = load_settings()
    data.update(changes)
    write_json(settings_path(), data)
    return data


def read_env() -> dict:
    """~/동화공방/.env를 읽는다. 빈 값과 주석은 건너뛴다."""
    try:
        lines = env_path().read_text(encoding="utf-8-sig").splitlines()
    except FileNotFoundError:
        return {}
    values = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        if value:
            values[name.strip()] = value
    return values


def secret(name: str) -> str | None:
    """환경 변수가 먼저, 없으면 ~/동화공방/.env"""
    return os.environ.get(name) or read_env().get(name)


def ensure_env_file() -> Path:
    """.env가 없으면 빈 칸이 있는 틀을 만든다. 나만 읽을 수 있게 한다."""
    path = env_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ENV_TEMPLATE, encoding="utf-8")
        if os.name != "nt":
            path.chmod(0o600)
    return path
