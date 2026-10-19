"""동화 공방이 쓰는 폴더와, 이 PC가 어떤 환경인지 알려 준다.
bootstrap.py가 패키지를 깔기 전에도 불러 써서, 표준 라이브러리만 쓴다."""
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
ASSETS = PLUGIN_ROOT / "assets"
REFERENCE = PLUGIN_ROOT / "reference"
WINDOWS_CMD = Path("/mnt/c/Windows/System32/cmd.exe")
WINDOWS_EXPLORER = Path("/mnt/c/Windows/explorer.exe")
WINDOWS_NOTEPAD = Path("/mnt/c/Windows/System32/notepad.exe")
# 윈도우가 파일 이름에 못 쓰는 글자와, 주소(URL)에서 뜻이 바뀌는 #·%
FORBIDDEN = re.compile(r'[\\/:*?"<>|#%\x00-\x1f]')
WINDOWS_PATH = re.compile(r"^[A-Za-z]:\\")


def home() -> Path:
    """사진·동화·설정을 두는 곳. STORYBOOK_HOME으로 바꿀 수 있다."""
    return Path(os.environ.get("STORYBOOK_HOME") or Path.home() / "동화공방")


def people_dir() -> Path:
    return home() / "인물"


def stories_dir() -> Path:
    return home() / "동화"


def venv_dir() -> Path:
    return home() / ".venv"


def venv_python() -> Path:
    return venv_dir() / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def system() -> str:
    """mac · windows · wsl · linux 중 하나"""
    if sys.platform == "darwin":
        return "mac"
    if os.name == "nt":
        return "windows"
    if "microsoft" in platform.uname().release.lower():
        return "wsl"
    return "linux"


def safe_name(text: str, limit: int = 60) -> str:
    """폴더·파일 이름으로 써도 되는 글. 한글과 띄어쓰기는 그대로 두고 금지 글자만 뺀다."""
    name = FORBIDDEN.sub("", str(text))
    name = re.sub(r"\s+", " ", name).strip().strip(".").strip()
    return name[:limit].strip() or "이름없음"


def local_path(text: str) -> Path:
    """터미널에 끌어다 놓은 파일 경로를 이 PC에서 열 수 있는 경로로 바꾼다.
    따옴표와 글자 앞 역슬래시(«\\ », Mac은 «\\(», «\\'»도 붙인다)를 걷어 내고,
    WSL에서는 윈도우 경로(C:\\...)를 /mnt/c/...로 바꾼다."""
    text = str(text).strip().strip("'\"")
    if WINDOWS_PATH.match(text):
        if system() == "wsl":
            out = subprocess.run(["wslpath", "-u", text], capture_output=True, text=True, check=True).stdout
            return Path(out.strip())
        return Path(text)
    if system() != "windows":
        text = re.sub(r"\\(.)", r"\1", text)
    return Path(os.path.expanduser(text))


def to_windows(path: Path) -> str:
    """WSL 경로를 윈도우 경로로 바꾼다 (WSL에서만 부른다)."""
    return subprocess.run(["wslpath", "-w", str(path)], capture_output=True, text=True, check=True).stdout.strip()


def windows_home() -> Path | None:
    """WSL에서 윈도우 사용자 폴더(/mnt/c/Users/이름). 못 찾으면 None"""
    if system() != "wsl" or not WINDOWS_CMD.exists():
        return None
    try:
        # /u를 주면 cmd.exe가 UTF-16으로 내보낸다. 안 주면 cp949라서 한글 사용자 이름이 깨진다.
        raw = subprocess.run([str(WINDOWS_CMD), "/u", "/c", "echo %USERPROFILE%"], capture_output=True,
                             cwd="/mnt/c", timeout=20).stdout
        out = raw.decode("utf-16-le", "replace").strip()
        if not out or "%" in out:
            return None
        path = Path(subprocess.run(["wslpath", "-u", out], capture_output=True, text=True, check=True).stdout.strip())
        return path if path.is_dir() else None
    except (OSError, subprocess.SubprocessError):
        return None


def open_file(path: Path) -> bool:
    """파일을 이 PC의 기본 프로그램(HTML이면 브라우저)으로 연다. 못 열면 False"""
    kind = system()
    try:
        if kind == "mac":
            subprocess.Popen(["open", str(path)])
        elif kind == "windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif kind == "wsl":
            explorer = shutil.which("explorer.exe") or str(WINDOWS_EXPLORER)
            subprocess.Popen([explorer, to_windows(path)], cwd="/mnt/c")
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def open_text(path: Path) -> bool:
    """글 편집기(메모장 등)로 연다. .env에 비밀값을 넣을 때 쓴다."""
    kind = system()
    try:
        if kind == "mac":
            subprocess.Popen(["open", "-t", str(path)])
        elif kind == "windows":
            subprocess.Popen(["notepad.exe", str(path)])
        elif kind == "wsl":
            notepad = shutil.which("notepad.exe") or str(WINDOWS_NOTEPAD)
            subprocess.Popen([notepad, to_windows(path)], cwd="/mnt/c")
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except (OSError, subprocess.SubprocessError):
        return False
