"""동화 공방 준비: Python·ffmpeg를 보고, ~/동화공방/.venv에 필요한 패키지를 깐다.
표준 라이브러리만 쓴다. 다른 스크립트보다 먼저 돈다.

  python3 bootstrap.py          검사하고, 없는 패키지를 깐다
  python3 bootstrap.py --check  검사만 한다
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# 윈도우 Python은 파이프에 시스템 코드 페이지(한국어 윈도우는 cp949)로 써서 ✓·« »에서 죽는다.
# Claude Code는 출력을 UTF-8로 읽으니 처음부터 UTF-8로 맞춘다.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from storybook import paths  # noqa: E402  (paths는 표준 라이브러리만 쓴다)

PACKAGES = ["pillow>=10", "pillow-heif>=0.16", "edge-tts>=6.1", "pyyaml>=6"]
MODULES = ["PIL", "pillow_heif", "edge_tts", "yaml"]
MIN_PYTHON = (3, 9)
HINTS = {
    "ffmpeg": {
        "mac": "brew install ffmpeg",
        "windows": "winget install Gyan.FFmpeg  (설치한 뒤 Claude Code를 껐다가 다시 켜야 ffmpeg가 보여요)",
        "wsl": "sudo apt install -y ffmpeg",
        "linux": "sudo apt install -y ffmpeg  (배포판에 맞는 패키지 관리자로)",
    },
    "venv": {
        "mac": "brew install python",
        "windows": "winget install Python.Python.3.12",
        "wsl": "sudo apt install -y python3-venv",
        "linux": "sudo apt install -y python3-venv",
    },
}


def hint(tool: str) -> str:
    return HINTS[tool][paths.system()]


def missing_tools() -> list[str]:
    return [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]


def venv_ready() -> bool:
    python = paths.venv_python()
    if not python.exists():
        return False
    return subprocess.run([str(python), "-c", "import " + ", ".join(MODULES)], capture_output=True).returncode == 0


def make_venv() -> None:
    """uv가 있으면 uv로(빠르고 ensurepip가 필요 없다), 없으면 python -m venv로 만든다."""
    target = paths.venv_dir()
    if target.exists():
        shutil.rmtree(target)  # 반쯤 만들다 만 환경은 지우고 새로 만든다
    target.parent.mkdir(parents=True, exist_ok=True)
    uv = shutil.which("uv")
    if uv:
        subprocess.run([uv, "venv", "--quiet", "--python", sys.executable, str(target)], check=True)
        subprocess.run([uv, "pip", "install", "--quiet", "--python", str(paths.venv_python()), *PACKAGES], check=True)
    else:
        subprocess.run([sys.executable, "-m", "venv", str(target)], check=True)
        subprocess.run([str(paths.venv_python()), "-m", "pip", "install", "--quiet", *PACKAGES], check=True)


def main(argv: list[str]) -> int:
    version = sys.version.split()[0]
    if sys.version_info < MIN_PYTHON:
        print(f"✗ Python {version}: 3.9 이상이 필요해요. 설치: {hint('venv')}")
        return 2
    print(f"✓ Python {version}")

    problems = 0
    missing = missing_tools()
    if missing:
        print(f"✗ {', '.join(missing)}가 없어요. 설치: {hint('ffmpeg')}")
        problems += 1
    else:
        print("✓ ffmpeg")

    if venv_ready():
        print(f"✓ Python 패키지 ({paths.venv_dir()})")
    elif "--check" in argv:
        print("✗ Python 패키지가 아직 안 깔렸어요")
        problems += 1
    else:
        print("… Python 패키지를 까는 중이에요 (1~2분)")
        try:
            make_venv()
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"✗ 패키지를 깔지 못했어요 ({e}). 이걸 먼저 깔고 다시 해 주세요: {hint('venv')}")
            return 2
        if not venv_ready():
            print(f"✗ 패키지를 깔았는데 불러오지 못했어요. {hint('venv')} 뒤에 다시 해 주세요")
            return 2
        print(f"✓ Python 패키지 ({paths.venv_dir()})")
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
