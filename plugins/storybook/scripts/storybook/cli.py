"""sb.py 명령들. SKILL.md가 부르는 이름과 옵션이 여기 있다.
끝 코드: 0 됨 · 1 입력을 고쳐야 함 · 2 준비가 안 됨(→ /storybook:setup) · 3 사람에게 물어야 함(사용량 한도, 잔액 등)"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import signal
import sys
from pathlib import Path

from . import codex as codex_engine
from . import config, painter, pages, paths, people, sheet, story, video, voice


class NotReady(Exception):
    pass


def say(text: str) -> None:
    print(text, flush=True)


def folder_arg(text: str | None) -> Path:
    if not text:
        raise story.StoryError(["동화 폴더를 적어 주세요 (sb.py story list로 찾아요)"])
    path = paths.local_path(text)
    if not path.is_absolute():
        path = paths.stories_dir() / text.strip()
    if not (path / "story.json").exists():
        raise story.StoryError([f"동화 폴더를 찾지 못했어요: {text} (sb.py story list로 찾아요)"])
    return path


def pages_arg(text: str | None) -> list[int] | None:
    if not text:
        return None
    try:
        return sorted({int(x) for x in text.replace(" ", "").split(",") if x})
    except ValueError as e:
        raise story.StoryError([f"쪽 번호는 3,5처럼 적어요: {text}"]) from e


def not_while_drawing(folder: Path) -> Path:
    """그리는 중에 목소리·MP4를 만들면 그린 결과를 옛 story.json으로 덮어써서 기다리게 한다"""
    if painter.drawing(folder):
        raise painter.PaintError("지금 그림을 그리는 중이에요. 다 그렸다는 말이 나온 뒤에 해 주세요")
    return folder


def chosen_image_engine() -> str:
    name = config.load_settings().get("image")
    if name not in ("codex", "fal"):
        raise NotReady("그림 엔진을 아직 안 골랐어요. /storybook:setup으로 골라 주세요")
    return name


def make_engine(name: str | None):
    if name == "codex":
        return codex_engine.CodexEngine()
    if name == "fal":
        from .fal import FalEngine
        return FalEngine()
    raise NotReady("그림 엔진을 아직 안 골랐어요. /storybook:setup으로 골라 주세요")


def cmd_doctor(args) -> int:
    s = config.load_settings()
    lines = [f"동화 공방 준비 상태 ({paths.home()})", "✓ Python 패키지"]
    ready = True

    def mark(good: bool, yes: str, no: str) -> None:
        nonlocal ready
        ready = ready and good
        lines.append(f"✓ {yes}" if good else f"✗ {no}")

    mark(bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), "ffmpeg", "ffmpeg가 없어요 → /storybook:setup")
    mark(bool(s.get("consent")), f"사진 안내 동의 ({s.get('consent')})",
         "사진 안내에 아직 동의하지 않았어요 → /storybook:setup")
    image = s.get("image")
    if image == "codex":
        cmd = codex_engine.find()
        logged = bool(cmd) and codex_engine.login_status(cmd)[0]
        mark(logged, "그림: Codex (ChatGPT 로그인)",
             "그림: Codex를 찾지 못했어요 → reference/setup-image.md" if not cmd
             else "그림: Codex가 ChatGPT 계정으로 로그인돼 있지 않아요 → codex login")
    elif image == "fal":
        mark(bool(config.secret("FAL_KEY")), "그림: fal.ai (FAL_KEY 있음)",
             "그림: fal.ai를 골랐는데 FAL_KEY가 없어요 → sb.py env open")
    else:
        mark(False, "", "그림 엔진을 아직 안 골랐어요 → /storybook:setup")
    chosen = s.get("voice") or {}
    if chosen.get("engine") == "fish":
        mark(bool(config.secret("FISH_AUDIO_API_KEY") and config.secret("FISH_VOICE_ID")),
             "목소리: Fish Audio (키·목소리 ID 있음)", "목소리: Fish Audio 키나 목소리 ID가 없어요 → sb.py env open")
    elif chosen.get("engine") == "edge":
        mark(True, f"목소리: 기본 목소리 {voice.VOICES.get(chosen.get('voice'), chosen.get('voice'))}", "")
    else:
        mark(False, "", "목소리를 아직 안 골랐어요 → /storybook:setup")
    say("\n".join(lines))
    return 0 if ready else 2


def cmd_settings(args) -> int:
    if args.what == "show":
        say(json.dumps(config.load_settings(), ensure_ascii=False, indent=2))
    elif args.what == "image":
        if args.value not in ("codex", "fal"):
            raise story.StoryError(["그림 엔진은 codex 또는 fal이에요"])
        config.save_settings(image=args.value)
        say(f"그림 엔진: {args.value}")
    elif args.what == "voice":
        if args.value == "fish":
            config.save_settings(voice={"engine": "fish"})
            say("목소리: Fish Audio")
            return 0
        name = args.name or voice.DEFAULT_VOICE
        if args.value != "edge" or name not in voice.VOICES:
            raise story.StoryError([f"목소리는 fish 또는 edge예요. edge 목소리: {', '.join(voice.VOICES)}"])
        config.save_settings(voice={"engine": "edge", "voice": name})
        say(f"목소리: {voice.VOICES[name]}")
    elif args.what == "consent":
        day = datetime.date.today().isoformat()
        config.save_settings(consent=day)
        say(f"사진 안내 동의: {day}")
    return 0


def cmd_env(args) -> int:
    path = config.ensure_env_file()
    say(f"비밀값 파일: {path}")
    if paths.open_text(path):
        say("편집기로 열었어요. 쓰는 엔진의 줄에서 = 뒤에 붙여 넣고 저장한 다음 알려 주세요.")
    else:
        say("편집기를 열지 못했어요. 위 파일을 직접 열어 주세요.")
    return 0


def cmd_codex(args) -> int:
    cmd = codex_engine.find()
    if not cmd:
        say("✗ Codex를 찾지 못했어요. reference/setup-image.md의 Codex 설치를 해 주세요")
        return 2
    logged, said = codex_engine.login_status(cmd)
    say(f"Codex: {' '.join(cmd)}\n{said}")
    say("✓ ChatGPT 계정으로 로그인돼 있어요" if logged
        else "✗ ChatGPT 계정으로 로그인해 주세요: codex login (API 키 로그인은 쓰지 않아요)")
    return 0 if logged else 2


def cmd_fish(args) -> int:
    key, voice_id = config.secret("FISH_AUDIO_API_KEY"), config.secret("FISH_VOICE_ID")
    if not key or not voice_id:
        say("✗ FISH_AUDIO_API_KEY와 FISH_VOICE_ID를 넣어 주세요 (sb.py env open)")
        return 2
    visibility = voice.fish_visibility(key, voice_id)
    if visibility == "private":
        say("✓ 목소리가 비공개예요")
        return 0
    say(f"! 목소리 공개 범위: {visibility}. 내 목소리를 복제한 거라면 Fish Audio에서 비공개로 바꿔 주세요")
    return 3


def cmd_people(args) -> int:
    if args.what == "list":
        found = people.list_people()
        if not found:
            say("저장한 인물이 없어요")
        for person in found:
            kind = person["kind_ko"] or ("아이" if person["role"] == "child" else "인형")
            age = f", {person['age']}살" if person.get("age") else ""
            say(f"{person['name']}\t{kind}{age}\t{person['photo']}")
    elif args.what == "add":
        if not (args.name and args.role and args.photo):
            raise people.PersonError("--name, --role, --photo가 다 있어야 해요")
        info = people.save_person(args.name, args.role, paths.local_path(args.photo), age=args.age)
        say(f"저장했어요: {info['name']} ({info['photo']})")
    elif args.what == "remove":
        people.remove_person(args.name or "")
        say(f"지웠어요: {args.name}")
    return 0


def _read_draft(target: str | None) -> dict:
    try:
        if target == "-":
            return json.loads(sys.stdin.read())
        return json.loads(paths.local_path(target or "").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise story.StoryError([f"초안 JSON을 읽지 못했어요: {e}"]) from e


def cmd_story(args) -> int:
    what = args.what
    if what == "themes":
        for theme in story.themes():
            say(f"{theme['key']}\t{theme['emoji']} {theme['label']}\t{theme['desc']}")
        return 0
    if what == "examples":
        say(story.examples(args.target or ""))
        return 0
    if what == "new":
        folder = story.create(_read_draft(args.target))
        say(f"만들었어요: {folder}")
        for line in story.check(story.load(folder))[1]:
            say(f"! {line}")
        return 0
    if what == "list":
        found = story.all_stories()
        if not found:
            say("아직 만든 동화가 없어요")
        for folder in found:
            say(story.summary(folder))
        return 0
    folder = folder_arg(args.target)
    if what == "check":
        errors, warnings = story.check(story.load(folder))
        for line in errors:
            say(f"✗ {line}")
        for line in warnings:
            say(f"! {line}")
        if not errors and not warnings:
            say("✓ 고칠 곳이 없어요")
        return 1 if errors else 0
    if what == "show":
        data = story.load(folder)
        say(f"{data['title']}  ({folder})")
        for page in data["pages"]:
            state = "그림 있음" if page["image"] else "그림 없음"
            say(f"{story.label(page['n'])} [{state}, 목소리 {len(page['voices'])}개] {page['text']}")
        return 0
    if what == "edit":
        if args.page is None:
            raise story.StoryError(["고칠 쪽 번호를 적어 주세요 (0은 표지)"])
        page = story.edit(folder, args.page, text=args.text, prompt_en=args.prompt,
                          cast=args.cast.split(",") if args.cast else None, redraw=args.redraw, note=args.note or "")
        say(f"고쳤어요: {story.label(page['n'])}" + (" (다시 그릴 쪽)" if page["image"] is None else ""))
        return 0
    if what == "delete":
        story.delete(folder)
        say(f"지웠어요: {folder}")
    return 0


def cmd_draw(args) -> int:
    folder = folder_arg(args.folder)
    todo = painter.pending(story.load(folder), pages_arg(args.pages), folder)
    if not todo:
        say("그릴 쪽이 없어요. 다 그렸어요")
        return 0
    image = chosen_image_engine()
    if args.plan:
        names = ", ".join(story.label(p["n"]) for p in todo)
        if image == "fal":
            from .fal import estimate
            say(f"그릴 쪽: {names}\n엔진: fal.ai, {estimate(len(todo))}, 3분 안팎")
        else:
            say(f"그릴 쪽: {names}\n엔진: Codex, 추가 비용 없음, {len(todo) * 2}분쯤 (한 장에 1~3분)")
        return 0
    done = painter.draw(folder, make_engine(image), pages_arg(args.pages), progress=say)
    if done:
        say("다 그렸어요: " + ", ".join(story.label(n) for n in done))
    left = painter.pending(story.load(folder), pages_arg(args.pages), folder)
    if left:
        say("아직 안 그린 쪽: " + ", ".join(story.label(p["n"]) for p in left) + " (draw를 다시 하면 그려요)")
    return 0


def cmd_draw_test(args) -> int:
    """사진 없이 시험 그림 한 장. setup에서 엔진이 제대로 도는지 본다."""
    from PIL import Image, ImageDraw
    image = chosen_image_engine()
    engine = make_engine(image)
    root = paths.home() / ".assets"
    root.mkdir(parents=True, exist_ok=True)
    toy = root / "test-toy.jpg"
    canvas = Image.new("RGB", (600, 600), (250, 240, 220))
    pen = ImageDraw.Draw(canvas)
    for box in ((150, 150, 450, 450), (150, 90, 250, 190), (350, 90, 450, 190)):
        pen.ellipse(box, fill=(230, 140, 60))
    canvas.save(toy, "JPEG")
    prompt = "\n".join([painter.STYLE, "The toy friend from image 1 waving hello in a sunny meadow.",
                        "Image 1 is the reference photo of the toy friend: a round orange teddy bear.", painter.RULES])
    request = painter.Request(n=0, prompt=prompt, keys=["toy1"], photos=[toy], style=None, seed=7)
    say("시험 그림을 그리는 중이에요" + (" (Codex는 1~3분 걸려요)" if image == "codex" else ""))
    try:
        raw = engine.paint(request, 1)
    finally:
        engine.close()
    out = root / "test.jpg"
    out.write_bytes(painter.to_jpeg(raw))
    paths.open_file(out)
    say(f"✓ 시험 그림: {out}")
    return 0


def cmd_sheet(args) -> int:
    say(str(sheet.build(folder_arg(args.folder))))
    return 0


def cmd_voice(args) -> int:
    made = voice.narrate(not_while_drawing(folder_arg(args.folder)), progress=say)
    say(f"목소리 {made}개를 만들었어요" if made else "목소리는 이미 다 있어요")
    return 0


def cmd_voice_samples(args) -> int:
    page = pages.voice_page(voice.samples(paths.home() / ".assets" / "voices"))
    if not args.no_open:
        paths.open_file(page)
    say(f"목소리 고르기 화면: {page}")
    return 0


def cmd_video(args) -> int:
    path = video.build(not_while_drawing(folder_arg(args.folder)), music=args.music, progress=say)
    say(f"MP4: {path}")
    if paths.system() == "wsl":
        copied = video.copy_to_downloads(path)
        if copied:
            say(f"윈도우 다운로드 폴더에도 넣었어요: {copied}")
    return 0


def cmd_page(args) -> int:
    if args.kind == "voice":
        return cmd_voice_samples(args)
    path = pages.build(args.kind, folder_arg(args.folder))
    opened = False if args.no_open else paths.open_file(path)
    say(f"{pages.SCREEN[args.kind]} 화면: {path}")
    if not args.no_open and not opened:
        say("브라우저를 열지 못했어요. 위 파일을 직접 열어 주세요")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sb.py", description="동화 공방 명령")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, text):
        command = sub.add_parser(name, help=text)
        command.set_defaults(func=func)
        return command

    add("doctor", cmd_doctor, "준비 상태 보기")
    s = add("settings", cmd_settings, "고른 엔진 보기·바꾸기")
    s.add_argument("what", choices=["show", "image", "voice", "consent"])
    s.add_argument("value", nargs="?")
    s.add_argument("--name")
    add("env", cmd_env, "비밀값 파일(.env) 열기").add_argument("what", choices=["open"])
    add("codex", cmd_codex, "Codex 위치·로그인 확인").add_argument("what", choices=["check"])
    add("fish", cmd_fish, "Fish Audio 목소리 비공개 확인").add_argument("what", choices=["check"])
    s = add("people", cmd_people, "저장한 인물")
    s.add_argument("what", choices=["list", "add", "remove"])
    s.add_argument("--name")
    s.add_argument("--role", choices=["child", "toy"])
    s.add_argument("--photo")
    s.add_argument("--age", type=int)
    s = add("story", cmd_story, "동화 폴더")
    s.add_argument("what", choices=["themes", "examples", "new", "check", "show", "list", "edit", "delete"])
    s.add_argument("target", nargs="?")
    s.add_argument("page", nargs="?", type=int)
    for option in ("--text", "--prompt", "--cast", "--note"):
        s.add_argument(option)
    s.add_argument("--redraw", action="store_true")
    s = add("draw", cmd_draw, "그림 그리기")
    s.add_argument("folder")
    s.add_argument("--pages")
    s.add_argument("--plan", action="store_true")
    add("draw-test", cmd_draw_test, "시험 그림 한 장")
    add("sheet", cmd_sheet, "그림 9장 모아 보기").add_argument("folder")
    add("voice", cmd_voice, "목소리 만들기").add_argument("folder")
    add("voice-samples", cmd_voice_samples, "기본 목소리 들어 보기").add_argument("--no-open", action="store_true")
    s = add("video", cmd_video, "MP4 만들기")
    s.add_argument("folder")
    s.add_argument("--music", choices=["lullaby", "twinkle", "meadow", "off"])
    s = add("page", cmd_page, "확인 화면 열기")
    s.add_argument("kind", choices=["draft", "art", "book", "voice"])
    s.add_argument("folder", nargs="?")
    s.add_argument("--no-open", action="store_true")
    return parser


def _terminated(signum, frame):
    # Claude Code가 명령을 끄면(SIGTERM) 그냥 죽지 않고 finally를 돌게 한다. 아이 사진이 든 임시 폴더를 지우고 Codex를 끈다.
    raise SystemExit(128 + signum)


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    signal.signal(signal.SIGTERM, _terminated)
    try:
        return args.func(args)
    except (story.StoryError, people.PersonError, video.VideoError) as e:
        say(f"✗ {e}")
        return 1
    except NotReady as e:
        say(f"✗ {e}")
        return 2
    except (painter.PaintError, voice.VoiceError) as e:
        say(f"✗ {e}")
        return 3
    except Exception as e:  # 영어 Traceback 대신 한국어 한 줄로 알린다. 자세히 보려면 STORYBOOK_DEBUG=1
        if os.environ.get("STORYBOOK_DEBUG"):
            raise
        say(f"✗ 뜻밖의 문제가 생겼어요: {e.__class__.__name__}: {e}")
        return 1
