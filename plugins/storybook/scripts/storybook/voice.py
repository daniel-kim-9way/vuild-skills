"""동화 글을 목소리 mp3로 만든다.
  edge : 마이크로소프트 신경망 목소리(edge-tts). 키가 없고 무료다
  fish : Fish Audio에 만든 목소리(FISH_AUDIO_API_KEY + FISH_VOICE_ID). 실패하면 edge 선희로 읽는다
어느 쪽이든 글만 그 회사로 간다. 사진은 안 간다."""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from . import chunks, config, story

VOICES = {
    "ko-KR-SunHiNeural": "선희 (여)",
    "ko-KR-InJoonNeural": "인준 (남)",
    "ko-KR-HyunsuMultilingualNeural": "현수 (남)",
}
DEFAULT_VOICE = "ko-KR-SunHiNeural"
RATE = "-8%"
FISH_URL = "https://api.fish.audio/v1/tts"
FISH_MODEL = "s2.1-pro-free"
SAMPLE = "옛날 옛날, 숲속 작은 집에 아기 곰 뭉치가 살았어요. 뭉치는 아침마다 창문을 열고 “안녕!” 하고 인사했어요."


class VoiceError(Exception):
    pass


def speak_edge(text: str, dest: Path, voice: str = DEFAULT_VOICE) -> None:
    import edge_tts

    try:
        asyncio.run(edge_tts.Communicate(text, voice, rate=RATE).save(str(dest)))
    except Exception as e:  # edge_tts는 연결 오류를 여러 모양으로 낸다
        raise VoiceError(f"목소리를 만들지 못했어요 ({e.__class__.__name__})") from e
    if not dest.exists() or dest.stat().st_size < 500:
        raise VoiceError("목소리 파일이 비어 있어요")


def speak_fish(text: str, dest: Path, key: str, voice_id: str,
               opener=urllib.request.urlopen, wait=time.sleep) -> None:
    body = json.dumps({"text": text, "reference_id": voice_id, "format": "mp3"}).encode()
    for attempt in range(1, 4):
        req = urllib.request.Request(FISH_URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {key}", "model": FISH_MODEL, "Content-Type": "application/json"})
        try:
            with opener(req, timeout=60) as response:
                audio = response.read()
        except urllib.error.HTTPError as e:
            if (e.code == 429 or e.code >= 500) and attempt < 3:
                wait(2 * attempt)  # 서버가 바쁘면 조금 쉬었다가 다시
                continue
            raise VoiceError(f"Fish Audio 오류 {e.code}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < 3:
                wait(2 * attempt)
                continue
            raise VoiceError(f"Fish Audio에 연결하지 못했어요 ({e.__class__.__name__})") from e
        if len(audio) < 500:
            raise VoiceError("Fish Audio가 빈 소리를 보냈어요")
        dest.write_bytes(audio)
        return


def fish_visibility(key: str, voice_id: str, opener=urllib.request.urlopen) -> str:
    """목소리 공개 범위(private·public·unlist). 내 목소리를 복제했다면 private이어야 한다."""
    req = urllib.request.Request(f"https://api.fish.audio/model/{voice_id}", headers={"Authorization": f"Bearer {key}"})
    try:
        with opener(req, timeout=30) as response:
            return str(json.loads(response.read()).get("visibility", "unknown"))
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise VoiceError(f"Fish Audio에서 목소리 정보를 받지 못했어요 ({e.__class__.__name__})") from e


class Speaker:
    """settings.json의 voice 설정대로 읽는다. Fish가 한 번 실패하면 그 뒤로는 선희로 읽는다."""

    def __init__(self, setting: dict | None = None, edge=speak_edge, fish=speak_fish, warn: Callable = print):
        self.setting = setting or config.load_settings().get("voice") or {"engine": "edge", "voice": DEFAULT_VOICE}
        self.edge, self.fish, self.warn = edge, fish, warn
        self.fell_back = False

    def uses_fish(self) -> bool:
        return self.setting.get("engine") == "fish" and not self.fell_back

    def signature(self) -> str:
        """지금 어떤 목소리로 읽는지. story.json에 남겨 두고, 바뀌면 처음부터 다시 읽는다.
        Fish는 목소리 ID 값 대신 해시 앞 8자만 남긴다."""
        if self.uses_fish():
            voice_id = config.secret("FISH_VOICE_ID") or ""
            return "fish:" + hashlib.sha256(voice_id.encode()).hexdigest()[:8]
        chosen = self.setting.get("voice", DEFAULT_VOICE) if self.setting.get("engine") == "edge" else DEFAULT_VOICE
        return f"edge:{chosen}"

    def say(self, text: str, dest: Path) -> None:
        if self.uses_fish():
            key, voice_id = config.secret("FISH_AUDIO_API_KEY"), config.secret("FISH_VOICE_ID")
            try:
                if not key or not voice_id:
                    raise VoiceError("Fish Audio 키나 목소리 ID가 없어요")
                self.fish(text, dest, key, voice_id)
                return
            except VoiceError as e:
                self.warn(f"Fish Audio로 못 읽어서 기본 목소리(선희)로 읽어요: {e}")
                self.fell_back = True
        chosen = self.setting.get("voice", DEFAULT_VOICE) if self.setting.get("engine") == "edge" else DEFAULT_VOICE
        self.edge(text, dest, chosen)


def narrate(folder: Path, speaker: Speaker | None = None, progress: Callable[[str], None] = print) -> int:
    """문장마다 목소리 파일을 만든다. 이미 다 있는 쪽은 건너뛴다. 새로 만든 개수를 돌려준다."""
    folder = Path(folder)
    speaker = speaker or Speaker()
    data = story.load(folder)
    (folder / "목소리").mkdir(exist_ok=True)
    wanted = speaker.signature()
    if data.get("voice_by") != wanted:
        if data.get("voice_by"):
            progress("목소리가 바뀌어서 처음부터 다시 읽어요")
        for page in data["pages"]:
            page["voices"] = []
    made = 0
    by_fish: list[tuple[str, Path]] = []
    for page in data["pages"]:
        parts = chunks.for_page(page)
        existing = page.get("voices") or []
        if len(existing) == len(parts) and all((folder / v).exists() for v in existing):
            if wanted.startswith("fish"):  # 예전에 Fish로 읽어 둔 쪽. 이번에 Fish가 실패하면 선희로 다시 읽는다
                by_fish.extend((part, folder / rel) for part, rel in zip(parts, existing))
            continue
        files = []
        for i, part in enumerate(parts):
            rel = f"목소리/p{page['n']}-{i}.mp3"
            fish_before = speaker.uses_fish()
            speaker.say(part, folder / rel)
            if fish_before and speaker.uses_fish():
                by_fish.append((part, folder / rel))
            files.append(rel)
            made += 1
        page["voices"] = files
        story.save(folder, data)
        progress(f"목소리: {story.label(page['n'])}")
    if speaker.fell_back and by_fish:
        progress("한 동화 안에서 목소리가 섞이지 않게 앞쪽도 선희 목소리로 다시 읽어요")
        for part, path in by_fish:
            speaker.say(part, path)
    data["voice_by"] = speaker.signature()
    story.save(folder, data)
    return made


def samples(dest_dir: Path, edge=speak_edge) -> list[dict]:
    """기본 목소리 셋이 같은 문장을 읽은 파일. 한 번 만들면 다시 쓴다."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for voice_id, name in VOICES.items():
        path = dest_dir / f"{voice_id}.mp3"
        if not path.exists():
            edge(SAMPLE, path, voice_id)
        made.append({"id": voice_id, "label": name, "file": path})
    return made
