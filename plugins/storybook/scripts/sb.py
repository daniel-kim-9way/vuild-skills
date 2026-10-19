"""동화 공방 명령 입구. SKILL.md가 모든 일을 이 파일로 시킨다.

  python3 sb.py <명령> ...     (명령 목록: python3 sb.py --help)

필요한 패키지가 없는 Python으로 불리면 ~/동화공방/.venv의 Python으로 다시 실행한다.
그 환경도 없으면 bootstrap.py를 먼저 돌리라고 알려 준다.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# 윈도우 Python은 파이프에 시스템 코드 페이지(한국어 윈도우는 cp949)로 써서 ✓·« »에서 죽는다.
# Claude Code는 출력을 UTF-8로 읽으니 처음부터 UTF-8로 맞춘다.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def ensure_packages() -> None:
    try:
        import edge_tts  # noqa: F401
        import PIL  # noqa: F401
        import yaml  # noqa: F401
    except ImportError:
        from storybook import paths
        python = paths.venv_python()
        inside = Path(sys.prefix).resolve() == paths.venv_dir().resolve()
        if python.exists() and not inside:
            argv = [str(python), str(Path(__file__).resolve()), *sys.argv[1:]]
            if os.name == "nt":
                sys.exit(subprocess.call(argv))
            os.execv(str(python), argv)
        python3 = "py -3" if os.name == "nt" else "python3"
        print(f"아직 준비가 안 됐어요. 먼저 이걸 실행하세요: {python3} \"{HERE / 'bootstrap.py'}\"")
        sys.exit(2)


if __name__ == "__main__":
    ensure_packages()
    from storybook.cli import main
    sys.exit(main(sys.argv[1:]))
