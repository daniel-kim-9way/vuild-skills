"""Codex(ChatGPT 구독)에 내장된 image_gen으로 그림을 그린다. API 키 없이 구독으로 돈다.

찾는 순서: PATH의 codex → WSL이면 윈도우 쪽 codex(cmd.exe /c codex).
권한은 작업 폴더 쓰기(--sandbox workspace-write)만 준다. «모든 권한 허용» 옵션은 쓰지 않는다.
Codex를 여럿 띄우면 만든 파일이 섞여서 한 번에 한 장씩 그린다(workers = 1).
Codex가 띄운 아래 프로세스까지 한 묶음으로 띄워서, 시간이 넘거나 그리기를 끌 때 묶음째 끈다.
"""
from __future__ import annotations

import os
import re
import secrets
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from . import config, paths
from .painter import PaintError, Request, RetryablePaintError

TIMEOUT = 600
PREFIX = "storybook-codex-"  # 임시 폴더 이름. 다른 프로그램 폴더와 헷갈리지 않게 길게 짓는다
LEFTOVER_AGE = 2 * 3600  # 이보다 오래된 임시 폴더는 강제로 꺼진 그리기가 남긴 것이다
# Codex가 API 키로 그리지 않게(회사 규칙), 다른 엔진의 키도 Codex에 넘기지 않는다
HIDDEN = ("OPENAI_API_KEY", *config.SECRET_NAMES)
LIMIT = re.compile(r"usage limit|rate limit|quota", re.I)
INSTRUCTIONS = """You are an image generator runner. Use the built-in image_gen tool via your Codex ChatGPT login.

STRICT:
- Do NOT use the OPENAI_API_KEY CLI fallback (scripts/image_gen.py). Do NOT write code or draw with PIL.
- {count} images are attached in order (image 1, image 2, ...). Use them only as references for how the characters look.{style}
- Generate exactly ONE new illustration, 1536x1024 landscape.
- Copy the final PNG to this exact path: {target}
- When done, print only: DONE

IMAGE PROMPT:
{prompt}
"""
STYLE_NOTE = (" The last attached image is this book's cover illustration: "
              "match its art style, palette and character designs.")


def _windows(cmd: list[str]) -> bool:
    return cmd[0].endswith("cmd.exe")


def _env() -> dict:
    return {name: value for name, value in os.environ.items() if name not in HIDDEN}


def _sweep(parent: Path) -> None:
    """강제로 꺼진 지난 그리기가 남긴 임시 폴더(아이 사진이 들어 있다)를 지운다"""
    now = time.time()
    for old in parent.glob(PREFIX + "*"):
        try:
            if old.is_dir() and now - old.stat().st_mtime > LEFTOVER_AGE:
                shutil.rmtree(old, ignore_errors=True)
        except OSError:
            pass


def find() -> list[str] | None:
    exe = shutil.which("codex")
    if exe:
        return [exe]
    if paths.system() == "wsl" and paths.WINDOWS_CMD.exists():
        try:
            probe = subprocess.run([str(paths.WINDOWS_CMD), "/c", "where codex"], capture_output=True,
                                   cwd="/mnt/c", timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        if probe.returncode == 0:
            return [str(paths.WINDOWS_CMD), "/c", "codex"]
    return None


def login_status(cmd: list[str], runner=subprocess.run) -> tuple[bool, str]:
    """(ChatGPT 계정으로 로그인했는지, codex가 한 말). API 키 로그인은 False다(회사 규칙)."""
    try:
        result = runner([*cmd, "login", "status"], capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=60, cwd="/mnt/c" if _windows(cmd) else None, env=_env())
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    said = ((result.stdout or "") + (result.stderr or "")).strip()
    return result.returncode == 0 and "ChatGPT" in said, said


class CodexEngine:
    name = "codex"
    workers = 1

    def __init__(self, cmd: list[str] | None = None, runner=None):
        self.cmd = cmd or find()
        if not self.cmd:
            raise PaintError("Codex를 찾지 못했어요. /storybook:setup에서 Codex 준비를 다시 해 주세요")
        self.runner = runner or self._run
        self.proc: subprocess.Popen | None = None
        self.dir = self._make_dir()
        self.dir_arg = paths.to_windows(self.dir) if _windows(self.cmd) else str(self.dir)

    def _make_dir(self) -> Path:
        """영어 이름만 든 임시 폴더. 윈도우 Codex면 윈도우 쪽 임시 폴더에 만든다(한글 경로에서 꼬이지 않게)."""
        if _windows(self.cmd):
            home = paths.windows_home()
            if home is None:
                raise PaintError("윈도우 사용자 폴더를 찾지 못해서 Codex에 사진을 넘길 수 없어요")
            parent = home / "AppData" / "Local" / "Temp"
            _sweep(parent)
            folder = parent / f"{PREFIX}{secrets.token_hex(4)}"
            folder.mkdir(parents=True)
            return folder
        _sweep(Path(tempfile.gettempdir()))
        return Path(tempfile.mkdtemp(prefix=PREFIX))

    def _run(self, args: list[str], *, input: str, cwd: Path, timeout: float, env: dict, **_) -> subprocess.CompletedProcess:
        """subprocess.run처럼 돌린다. 다만 Codex를 새 프로세스 묶음으로 띄워서, 시간이 넘으면 묶음째 끈다."""
        group = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"  # type: ignore[attr-defined]
                 else {"start_new_session": True})
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, encoding="utf-8", errors="replace", cwd=cwd, env=env, **group)
        try:
            out, err = self.proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            self._stop()
            try:
                self.proc.communicate(timeout=10)
            except (subprocess.TimeoutExpired, ValueError, OSError):
                pass
            raise
        return subprocess.CompletedProcess(args, self.proc.returncode, out, err)

    def _stop(self) -> None:
        """돌고 있는 Codex와 그 아래 프로세스를 끈다"""
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                proc.kill()

    def command(self, files: list[str]) -> list[str]:
        attach = [arg for name in files for arg in ("-i", name)]
        return [*self.cmd, "exec", "--skip-git-repo-check", "--ephemeral", "--enable", "image_generation",
                "--cd", self.dir_arg, "--sandbox", "workspace-write", *attach, "-"]

    def instructions(self, request: Request, target: str, count: int) -> str:
        separator = "\\" if _windows(self.cmd) else "/"
        return INSTRUCTIONS.format(count=count, style=STYLE_NOTE if request.style else "",
                                   target=f"{self.dir_arg}{separator}{target}", prompt=request.prompt)

    def paint(self, request: Request, attempt: int) -> bytes:
        files = []
        for key, photo in zip(request.keys, request.photos):
            shutil.copyfile(photo, self.dir / f"{key}.jpg")
            files.append(f"{key}.jpg")
        if request.style:
            shutil.copyfile(request.style, self.dir / "style.jpg")
            files.append("style.jpg")
        target = f"page-{request.n}-{attempt}-{secrets.token_hex(3)}.png"
        try:
            result = self.runner(self.command(files), input=self.instructions(request, target, len(files)),
                                 capture_output=True, text=True, encoding="utf-8", errors="replace",
                                 cwd=self.dir, timeout=TIMEOUT, env=_env())
        except subprocess.TimeoutExpired as e:
            raise RetryablePaintError(f"Codex가 {TIMEOUT // 60}분 안에 그리지 못했어요") from e
        out = self.dir / target
        if out.exists() and out.stat().st_size > 1000:
            return out.read_bytes()
        said = (result.stdout or "") + (result.stderr or "")
        if LIMIT.search(said):
            raise PaintError("Codex 사용량 한도에 걸렸어요. 한도가 풀린 뒤 «이어서 그려 줘»라고 해 주세요")
        raise RetryablePaintError("Codex가 그림 파일을 만들지 못했어요")

    def close(self) -> None:
        """그리던 Codex가 있으면 끄고, 아이 사진이 임시 폴더에 남지 않게 지운다"""
        self._stop()
        shutil.rmtree(self.dir, ignore_errors=True)
