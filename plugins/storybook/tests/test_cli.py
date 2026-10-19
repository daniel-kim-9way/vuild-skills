import io
import json
import os
import shutil
import subprocess
import signal
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from storybook import cli, config, painter, story
from tests.helpers import HomeTestCase, draft, make_image, make_story

SB = Path(__file__).resolve().parents[1] / "scripts" / "sb.py"


class CliTest(HomeTestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def test_doctor_on_empty_home(self):
        with mock.patch("shutil.which", return_value="/usr/bin/tool"):
            code, out = self.run_cli("doctor")
        self.assertEqual(code, 2)
        self.assertIn("그림 엔진을 아직 안 골랐어요", out)
        self.assertIn("사진 안내에 아직 동의하지 않았어요", out)

    def test_doctor_ready_with_fal_never_prints_the_key(self):
        self.run_cli("settings", "consent")
        self.run_cli("settings", "image", "fal")
        self.run_cli("settings", "voice", "edge", "--name", "ko-KR-InJoonNeural")
        config.ensure_env_file().write_text("FAL_KEY=secret-value-123\n", encoding="utf-8")
        with mock.patch("shutil.which", return_value="/usr/bin/tool"):
            code, out = self.run_cli("doctor")
        self.assertEqual(code, 0, out)
        self.assertIn("인준", out)
        self.assertNotIn("secret-value-123", out)

    def test_bad_settings(self):
        self.assertEqual(self.run_cli("settings", "image", "gemini")[0], 1)
        self.assertEqual(self.run_cli("settings", "voice", "edge", "--name", "nobody")[0], 1)

    def test_people_and_story_flow(self):
        photo = make_image(self.tmp / "사진 폴더" / "아이.jpg")
        self.assertEqual(self.run_cli("people", "add", "--name", "서준", "--role", "child", "--age", "4",
                                      "--photo", f"'{photo}'")[0], 0)
        self.assertEqual(self.run_cli("people", "add", "--name", "뭉치", "--role", "toy", "--photo", str(photo))[0], 0)
        self.assertIn("서준", self.run_cli("people", "list")[1])
        draft_file = self.tmp / "draft.json"
        draft_file.write_text(json.dumps(draft(), ensure_ascii=False), encoding="utf-8")
        code, out = self.run_cli("story", "new", str(draft_file))
        self.assertEqual(code, 0, out)
        folder = story.all_stories()[0]
        self.assertEqual(self.run_cli("story", "edit", str(folder), "2", "--text", "짧아요.")[0], 0)
        code, out = self.run_cli("story", "check", folder.name)
        self.assertEqual(code, 0)
        self.assertIn("2쪽 글이 4자예요", out)
        self.assertIn("그림 0/9", self.run_cli("story", "list")[1])

    def test_broken_draft_json(self):
        bad = self.tmp / "bad.json"
        bad.write_text("{ 이건 JSON이 아니에요", encoding="utf-8")
        code, out = self.run_cli("story", "new", str(bad))
        self.assertEqual(code, 1)
        self.assertIn("초안 JSON", out)

    def test_draw_plan_tells_fal_cost(self):
        folder = make_story(images=False)
        config.save_settings(image="fal")
        code, out = self.run_cli("draw", str(folder), "--plan")
        self.assertEqual(code, 0)
        self.assertIn("9장, 720~1,170원쯤", out)

    def test_draw_without_engine_is_not_ready(self):
        folder = make_story(images=False)
        self.assertEqual(self.run_cli("draw", str(folder))[0], 2)

    def test_draw_stops_with_code_3_on_usage_limit(self):
        folder = make_story(images=False)
        config.save_settings(image="codex")

        class Limited:
            name = "limited"
            workers = 1

            def paint(self, request, attempt):
                raise painter.PaintError("Codex 사용량 한도에 걸렸어요")

            def close(self):
                pass

        with mock.patch.object(cli, "make_engine", return_value=Limited()):
            code, out = self.run_cli("draw", str(folder))
        self.assertEqual(code, 3)
        self.assertIn("사용량 한도", out)

    def test_page_without_opening(self):
        folder = make_story(images=True)
        code, out = self.run_cli("page", "art", str(folder), "--no-open")
        self.assertEqual(code, 0)
        self.assertTrue((folder / "2-그림확인.html").exists())

    def test_unknown_folder(self):
        self.assertEqual(self.run_cli("draw", "없는-폴더")[0], 1)


class EntryTest(unittest.TestCase):
    def test_help_runs(self):
        result = subprocess.run([sys.executable, str(SB), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("동화 공방", result.stdout)

    def test_python_without_packages_points_to_bootstrap(self):
        python = shutil.which("python3")
        if python is None or subprocess.run([python, "-c", "import PIL"], capture_output=True).returncode == 0:
            self.skipTest("Pillow가 없는 python3가 필요해요")
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, STORYBOOK_HOME=tmp)
            result = subprocess.run([python, str(SB), "doctor"], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("bootstrap.py", result.stdout)


class UnexpectedErrorTest(HomeTestCase):
    def test_unexpected_error_is_told_in_korean(self):
        out = io.StringIO()
        with mock.patch.object(cli, "cmd_doctor", side_effect=RuntimeError("boom")), redirect_stdout(out):
            code = cli.main(["doctor"])
        self.assertEqual(code, 1)
        self.assertIn("뜻밖의 문제", out.getvalue())
        self.assertIn("RuntimeError: boom", out.getvalue())
        self.assertNotIn("Traceback", out.getvalue())


class ConsoleEncodingTest(unittest.TestCase):
    """한국어 윈도우 Python은 파이프에 cp949로 써서 ✓·« »에서 죽는다. PYTHONIOENCODING으로 그 상황을 흉내 낸다."""

    def run_cp949(self, *argv):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, STORYBOOK_HOME=tmp, PYTHONIOENCODING="cp949")
            return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, env=env)

    def test_sb_prints_utf8(self):
        result = self.run_cp949(SB, "doctor")
        self.assertNotIn(b"UnicodeEncodeError", result.stderr)
        self.assertIn("✗", result.stdout.decode("utf-8"))

    def test_bootstrap_prints_utf8(self):
        result = self.run_cp949(SB.parent / "bootstrap.py", "--check")
        self.assertNotIn(b"UnicodeEncodeError", result.stderr)
        self.assertIn("✓ Python", result.stdout.decode("utf-8"))


@unittest.skipIf(os.name == "nt", "SIGTERM 보내기는 리눅스·Mac에서 시험해요")
class TerminateTest(HomeTestCase):
    def test_terminated_draw_test_cleans_up_photos_and_codex(self):
        # Claude Code가 명령을 끄면(SIGTERM) 아이 사진이 든 임시 폴더와 Codex가 남으면 안 된다
        config.save_settings(image="codex")
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "codex"
        fake.write_text(f"#!{sys.executable}\nimport os, time\n"
                        f"open({str(self.tmp / 'codex.pid')!r}, 'w').write(str(os.getpid()))\ntime.sleep(60)\n",
                        encoding="utf-8")
        fake.chmod(0o755)
        temp = self.tmp / "t"
        temp.mkdir()
        env = dict(os.environ, STORYBOOK_HOME=str(self.home), TMPDIR=str(temp),
                   PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
        proc = subprocess.Popen([sys.executable, str(SB), "draw-test"], env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        marker = self.tmp / "codex.pid"
        for _ in range(100):
            if marker.exists() and marker.read_text():
                break
            time.sleep(0.1)
        self.assertTrue(list(temp.glob("storybook-*")))
        proc.send_signal(signal.SIGTERM)
        proc.wait(10)
        from tests.test_codex import alive
        self.assertFalse(alive(int(marker.read_text())))
        self.assertEqual(list(temp.glob("storybook-*")), [])


class WhileDrawingTest(HomeTestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def test_voice_and_video_wait_while_drawing(self):
        folder = make_story(images=True)
        (folder / painter.LOCK_NAME).write_text(str(os.getpid()), encoding="utf-8")
        for command in ("voice", "video"):
            code, out = self.run_cli(command, str(folder))
            self.assertEqual(code, 3, command)
            self.assertIn("그리는 중", out)

    def test_draw_tells_which_pages_are_left(self):
        from tests.test_painter import FakeEngine
        folder = make_story(images=False)
        config.save_settings(image="codex")

        class EditsSamePage(FakeEngine):
            def paint(self, request, attempt):
                if request.n == 4:
                    story.edit(folder, 4, prompt_en="[child] and [toy1] counting stars on the roof.")
                return super().paint(request, attempt)

        with mock.patch.object(cli, "make_engine", return_value=EditsSamePage()):
            code, out = self.run_cli("draw", str(folder))
        self.assertEqual(code, 0)
        self.assertIn("아직 안 그린 쪽: 4쪽", out)
