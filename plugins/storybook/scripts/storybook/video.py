"""그림 위에 문장을 하나씩 얹은 MP4를 만든다. 앱 StoryVideo와 같은 모양이다.
문장마다 한 컷이고, 그 문장의 목소리가 나오는 동안 보인다. 장이 바뀔 때는 살짝 어두워졌다 밝아진다.
아래에는 오르골 음악을 깔고, 목소리가 나올 때는 음악을 줄인다."""
from __future__ import annotations

import functools
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from . import chunks, layout, paths, story

WIDTH, HEIGHT = 1280, 720
ART_WIDTH = 960
ART_LEFT = (WIDTH - ART_WIDTH) // 2
FPS = 25
FONT = paths.ASSETS / "Jua-Regular.ttf"  # 둥근 굵은 글꼴 (OFL 무료 글꼴)
WHITE = (255, 255, 255)
OUTLINE = (58, 36, 22)
SHADOW = (30, 18, 8)
CORAL = (238, 123, 90)
MUSIC = ("lullaby", "twinkle", "meadow")
MUSIC_VOLUME = 0.32
FADE = 0.35


class VideoError(Exception):
    pass


@functools.lru_cache(maxsize=16)
def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT), size)


# 주아체에 없는 글자는 네모(□)로 나온다. 비슷한 글자로 바꾸고, 바꿀 것이 없으면 뺀다.
SWAPS = {"…": "...", "‘": "'", "’": "'", "—": "-", "–": "-", "「": "“", "」": "”", "『": "“", "』": "”"}


def _mask(text: str) -> tuple:
    mask = font(40).getmask(text)
    return mask.size, bytes(mask)


@functools.lru_cache(maxsize=None)
def has_glyph(ch: str) -> bool:
    return _mask(ch) != _mask("\ue000")  # 사용자 영역 글자는 늘 «없는 글자» 모양으로 그려진다


def drawable(text: str) -> str:
    """주아체로 그릴 수 있는 글로 바꾼다. 영상에만 쓰고 story.json의 글은 그대로 둔다."""
    text = re.sub(r"\s*·\s*", ", ", str(text))
    text = "".join(SWAPS.get(ch, ch) for ch in text)
    text = "".join(ch for ch in text if ch.isspace() or has_glyph(ch))
    return re.sub(r"[ \t]{2,}", " ", text).strip()


def _fill(words: list[str], size: int, width: int) -> list[str]:
    lines: list[str] = []
    for word in words:
        joined = f"{lines[-1]} {word}" if lines else None
        if joined and font(size).getlength(joined) <= width:
            lines[-1] = joined
        else:
            lines.append(word)
    return lines


def wrap(text: str, size: int, max_width: int) -> list[str]:
    """띄어쓰기 단위로 줄을 나눈다. 줄 수는 그대로 두고 가장 좁은 폭을 찾아,
    마지막 줄에 한 낱말만 남지 않게 줄 길이를 고르게 한다."""
    words = str(text).split()
    lines = _fill(words, size, max_width)
    if len(lines) <= 1:
        return lines
    low, high, best = max_width // 3, max_width, lines
    for _ in range(8):
        middle = (low + high) // 2
        trial = _fill(words, size, middle)
        if len(trial) <= len(lines):
            best, high = trial, middle
        else:
            low = middle
    return best


def outlined(text: str, size: int, max_width: int, align: str = "centre", fill=WHITE) -> Image.Image:
    """흰 글자 + 진한 윤곽선 + 옅은 그림자 (투명 바탕 RGBA)"""
    face = font(size)
    lines = wrap(drawable(text), size, max_width) or [""]
    stroke = max(round(size * 0.13), 3)
    spacing = round(size * 0.3)
    pad = stroke * 3
    ascent, descent = face.getmetrics()
    line_height = ascent + descent
    widths = [face.getlength(line) for line in lines]
    widest = max(widths)
    width = int(widest) + pad * 2
    height = line_height * len(lines) + spacing * (len(lines) - 1) + pad * 2 + stroke
    spots = []
    for i, line_width in enumerate(widths):
        if align == "centre":
            x = pad + (widest - line_width) / 2
        elif align == "right":
            x = pad + widest - line_width
        else:
            x = pad
        spots.append((x, pad + i * (line_height + spacing)))

    # 그림자: 윤곽선까지 그린 글자 모양을 흐리게 해서 조금 아래에 깐다
    mask = Image.new("L", (width, height), 0)
    pen = ImageDraw.Draw(mask)
    for (x, y), line in zip(spots, lines):
        pen.text((x, y), line, font=face, fill=255, stroke_width=stroke, stroke_fill=255)
    blurred = mask.filter(ImageFilter.GaussianBlur(stroke)).point(lambda v: int(v * 0.45))
    shifted = Image.new("L", (width, height), 0)
    shifted.paste(blurred, (0, stroke))
    shadow = Image.new("RGBA", (width, height), SHADOW + (0,))
    shadow.putalpha(shifted)

    letters = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pen = ImageDraw.Draw(letters)
    for (x, y), line in zip(spots, lines):
        pen.text((x, y), line, font=face, fill=tuple(fill) + (255,), stroke_width=stroke, stroke_fill=OUTLINE + (255,))
    return Image.alpha_composite(shadow, letters)


def _stack(parts: list[Image.Image]) -> Image.Image:
    width = max(p.width for p in parts)
    out = Image.new("RGBA", (width, sum(p.height for p in parts)), (0, 0, 0, 0))
    y = 0
    for part in parts:
        out.alpha_composite(part, ((width - part.width) // 2, y))
        y += part.height
    return out


def art_base(image_path: Path) -> Image.Image:
    """흐리게 늘린 그림을 바탕에 깔고, 가운데에 4:3 그림을 놓는다"""
    with Image.open(image_path) as opened:
        art = opened.convert("RGB")
    background = ImageOps.fit(art, (WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(18))
    background = ImageEnhance.Brightness(background).enhance(0.7)
    background.paste(ImageOps.fit(art, (ART_WIDTH, HEIGHT)), (ART_LEFT, 0))
    return background


def draw_chunk(base: Image.Image, text: str, zone: str, cast_line: str | None = None) -> Image.Image:
    """글을 바탕 없이 그림 위 정해진 자리에 얹는다. 표지는 제목 아래에 주인공 이름을 단다."""
    cover = cast_line is not None
    left, _top, width, _height = layout.ZONES.get(zone, layout.ZONES["top"])
    wide = zone in layout.WIDE
    align = "centre" if wide or cover else ("right" if zone.endswith("right") else "left")
    max_width = round((0.88 if wide else width) * ART_WIDTH)
    parts = [outlined(text, 68 if cover else 44, max_width, align)]
    if cover:
        parts.append(outlined(cast_line, 26, max_width, "centre"))
    body = _stack(parts)
    if wide:
        x = ART_LEFT + (ART_WIDTH - body.width) // 2
    elif zone.endswith("left"):
        x = ART_LEFT + round(left * ART_WIDTH)
    else:
        x = ART_LEFT + round((left + width) * ART_WIDTH) - body.width
    y = round(0.03 * HEIGHT) if zone.startswith("top") else HEIGHT - round(0.03 * HEIGHT) - body.height
    x = max(0, min(x, WIDTH - body.width))
    y = max(0, min(y, HEIGHT - body.height))
    frame = base.convert("RGBA")
    frame.alpha_composite(body, (x, y))
    return frame.convert("RGB")


def end_card(data: dict, folder: Path) -> Image.Image:
    base = art_base(folder / data["pages"][0]["image"]).filter(ImageFilter.GaussianBlur(6))
    base = ImageEnhance.Brightness(base).enhance(0.8)
    parts = [outlined("끝", 120, 600, "centre", fill=CORAL)]
    if data.get("lesson"):
        parts.append(outlined(data["lesson"], 38, 900, "centre"))
    body = _stack(parts)
    frame = base.convert("RGBA")
    frame.alpha_composite(body, ((WIDTH - body.width) // 2, (HEIGHT - body.height) // 2))
    return frame.convert("RGB")


def cast_line(data: dict) -> str:
    return "주인공: " + ", ".join(member["name"] for member in data["cast"])


def probe(path: Path) -> float:
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        seconds = float(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return 3.0
    return seconds if seconds > 0 else 3.0


def shots(folder: Path, data: dict, workdir: Path) -> list[dict]:
    """컷 목록: 문장마다 한 컷 + 끝 컷. 글 자리(zones)가 없으면 여기서 정해 story.json에 남긴다."""
    missing = [story.label(p["n"]) for p in data["pages"] if not p["image"] or not (folder / p["image"]).exists()]
    if missing:
        raise VideoError("그림이 없는 쪽이 있어요: " + ", ".join(missing) + ". 먼저 그려 주세요")
    result = []
    for page in data["pages"]:
        parts = chunks.for_page(page)
        image = folder / page["image"]
        if len(page.get("zones") or []) != len(parts):
            page["zones"] = layout.zones(image, parts, cover=page["n"] == 0)
        base = art_base(image)
        voices = page.get("voices") or []
        for i, part in enumerate(parts):
            frame = workdir / f"frame-{page['n']}-{i}.png"
            draw_chunk(base, part, page["zones"][i], cast_line(data) if page["n"] == 0 else None).save(frame)
            audio = folder / voices[i] if len(voices) == len(parts) and (folder / voices[i]).exists() else None
            last = i == len(parts) - 1
            speech = probe(audio) if audio else max(3.0, len(part) * 0.13)
            result.append({"frame": frame, "audio": audio, "duration": round(0.5 + speech + (1.2 if last else 0.6), 2),
                           "fade_in": i == 0, "fade_out": last})
    ending = workdir / "frame-end.png"
    end_card(data, folder).save(ending)
    result.append({"frame": ending, "audio": None, "duration": 4.0, "fade_in": True, "fade_out": True})
    return result


def run_ffmpeg(*args) -> None:
    try:
        result = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *[str(a) for a in args]], capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=180)
    except subprocess.TimeoutExpired as e:
        raise VideoError("영상을 만드는 데 너무 오래 걸렸어요") from e
    except FileNotFoundError as e:
        raise VideoError("ffmpeg가 없어요. /storybook:setup을 먼저 해 주세요") from e
    if result.returncode != 0:
        raise VideoError("ffmpeg 오류: " + " ".join(result.stderr.strip().splitlines()[-2:])[:200])


def segment(shot: dict, path: Path) -> None:
    duration = shot["duration"]
    fades = []
    if shot["fade_in"]:
        fades.append(f"fade=t=in:st=0:d={FADE}")
    if shot["fade_out"]:
        fades.append(f"fade=t=out:st={round(duration - FADE, 2)}:d={FADE}")
    picture = ",".join([*fades, "format=yuv420p"])
    if shot["audio"]:
        sound_input = ["-i", shot["audio"]]
    else:
        sound_input = ["-f", "lavfi", "-t", duration, "-i", "anullsrc=r=44100:cl=stereo"]
    sound = f"adelay=500:all=1,apad,atrim=0:{duration},aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo"
    run_ffmpeg("-loop", "1", "-framerate", FPS, "-t", duration, "-i", shot["frame"], *sound_input,
               "-filter_complex", f"[0:v]{picture}[v];[1:a]{sound}[a]", "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "20", "-r", FPS,
               "-c:a", "aac", "-b:a", "160k", "-t", duration, path)


def concat(segments: list[Path], workdir: Path) -> Path:
    listing = workdir / "list.txt"
    # ffmpeg 목록은 '로 감싸니, 경로 안의 '는 '\''로 적는다 (윈도우 사용자 이름에 '가 있을 수 있다)
    quoted = (path.as_posix().replace("'", "'\\''") for path in segments)
    listing.write_text("".join(f"file '{path}'\n" for path in quoted), encoding="utf-8")
    joined = workdir / "joined.mp4"
    run_ffmpeg("-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined)
    return joined


def add_music(joined: Path, workdir: Path, total: float, music: str) -> Path:
    """오르골 음악을 깔고, 목소리가 나올 때는 음악을 줄인다"""
    final = workdir / "final.mp4"
    if music == "off":
        run_ffmpeg("-i", joined, "-c", "copy", "-movflags", "+faststart", final)
        return final
    track = paths.ASSETS / "music" / f"{music}.flac"
    graph = (f"[1:a]aresample=44100,aformat=channel_layouts=stereo,aecho=0.8:0.7:40|90:0.25|0.15,"
             f"volume={MUSIC_VOLUME},afade=t=in:d=2[m];"
             "[0:a]asplit=2[voice][key];[m][key]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[duck];"
             f"[voice][duck]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={round(total - 2, 2)}:d=2[a]")
    run_ffmpeg("-i", joined, "-stream_loop", "-1", "-i", track, "-filter_complex", graph, "-map", "0:v", "-map", "[a]",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", round(total, 2), final)
    return final


def silent_pages(folder: Path, data: dict) -> list[str]:
    """목소리 파일이 다 있지 않은 쪽 이름"""
    names = []
    for page in data["pages"]:
        voices = page.get("voices") or []
        if len(voices) != len(chunks.for_page(page)) or not all((folder / v).exists() for v in voices):
            names.append(story.label(page["n"]))
    return names


def build(folder: Path, music: str | None = None, progress: Callable[[str], None] = print) -> Path:
    """MP4를 만들고 경로를 돌려준다. 파일 이름은 제목이다."""
    folder = Path(folder)
    data = story.load(folder)
    music = music or data.get("music") or "lullaby"
    if music != "off" and music not in MUSIC:
        raise VideoError(f"음악은 {', '.join(MUSIC)}, off 중 하나예요: {music}")
    data["music"] = music
    target = story.video_path(folder, data)
    silent = silent_pages(folder, data)
    if silent:
        progress(f"목소리 없이 넣은 쪽: {', '.join(silent)} (목소리를 먼저 만들면 읽어 줘요)")
    with tempfile.TemporaryDirectory(prefix="storybook-video-") as tmp:
        workdir = Path(tmp)
        progress("컷을 그리는 중이에요")
        cuts = shots(folder, data, workdir)
        story.save(folder, data)  # 새로 정한 글 자리와 음악을 남긴다
        progress(f"영상 조각 {len(cuts)}개를 만드는 중이에요")
        pieces = [workdir / f"seg-{i:03d}.mp4" for i in range(len(cuts))]
        with ThreadPoolExecutor(3) as pool:
            list(pool.map(segment, cuts, pieces))
        final = add_music(concat(pieces, workdir), workdir, sum(c["duration"] for c in cuts), music)
        try:
            shutil.move(str(final), str(target))
        except PermissionError as e:
            raise VideoError(f"{target.name} 파일이 동영상 플레이어 같은 다른 프로그램에서 열려 있어요. "
                             "닫고 다시 해 주세요") from e
    for old in folder.glob("*.mp4"):  # 제목을 바꾸면 옛 이름의 MP4가 남지 않게 지운다
        if old != target:
            try:
                old.unlink()
            except OSError:
                pass
    return target


def copy_to_downloads(path: Path) -> Path | None:
    """WSL이면 윈도우 다운로드 폴더에도 복사한다. 못 찾으면 None"""
    home = paths.windows_home()
    if home is None or not (home / "Downloads").is_dir():
        return None
    target = home / "Downloads" / path.name
    shutil.copyfile(path, target)
    return target
