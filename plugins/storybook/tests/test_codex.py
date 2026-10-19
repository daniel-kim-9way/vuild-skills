import dataclasses
import os
import sys
import threading
import time
import unittest
import re
import subprocess
from pathlib import Path
from unittest import mock

from storybook import codex, painter, story
from storybook.painter import PaintError, RetryablePaintError
from tests.helpers import HomeTestCase, make_image, make_story
from tests.test_painter import png


class CodexTest(HomeTestCase):
    def setUp(self):
        super().setUp()
        self.folder = make_story(images=False)
        data = story.load(self.folder)
        self.request = painter.request_for(data, data["pages"][0], self.folder)

    def engine(self, runner):
        engine = codex.CodexEngine(cmd=["codex"], runner=runner)
        self.addCleanup(engine.close)  # 임시 폴더가 /tmp에 남지 않게
        return engine

    def test_command_never_bypasses_sandbox(self):
        engine = self.engine(runner=None)
        cmd = engine.command(["child.jpg", "toy1.jpg"])
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", cmd)
        self.assertEqual(cmd[cmd.index("--sandbox") + 1], "workspace-write")
        self.assertEqual(cmd[-5:], ["-i", "child.jpg", "-i", "toy1.jpg", "-"])
        engine.close()

    def test_paint_returns_the_file_codex_wrote_and_close_cleans_up(self):
        seen = {}

        def runner(cmd, input, cwd, **kwargs):
            seen["input"] = input
            seen["files"] = sorted(p.name for p in Path(cwd).iterdir())
            target = re.search(r"exact path: (.+)", input).group(1).strip()
            Path(target).write_bytes(png())
            return subprocess.CompletedProcess(cmd, 0, "DONE", "")

        engine = self.engine(runner)
        self.assertGreater(len(engine.paint(self.request, 1)), 1000)
        self.assertIn("Do NOT use the OPENAI_API_KEY", seen["input"])
        self.assertIn("2 images are attached", seen["input"])
        self.assertEqual(seen["files"], ["child.jpg", "toy1.jpg"])
        workdir = engine.dir
        engine.close()
        self.assertFalse(workdir.exists())

    def test_style_reference_goes_last(self):
        seen = {}

        def runner(cmd, input, cwd, **kwargs):
            seen["cmd"] = cmd
            seen["input"] = input
            Path(re.search(r"exact path: (.+)", input).group(1).strip()).write_bytes(png())
            return subprocess.CompletedProcess(cmd, 0, "DONE", "")

        cover = make_image(self.tmp / "cover.jpg")
        engine = self.engine(runner)
        engine.paint(dataclasses.replace(self.request, n=3, style=cover), 1)
        self.assertEqual(seen["cmd"][-3:], ["-i", "style.jpg", "-"])
        self.assertIn("cover illustration", seen["input"])
        engine.close()

    def test_usage_limit_stops_and_asks(self):
        def runner(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 1, "", "You've hit your usage limit. Try again later.")

        with self.assertRaises(PaintError) as caught:
            self.engine(runner).paint(self.request, 1)
        self.assertNotIsInstance(caught.exception, RetryablePaintError)
        self.assertIn("사용량 한도", str(caught.exception))

    def test_no_file_is_retryable(self):
        def runner(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "DONE", "")

        with self.assertRaises(RetryablePaintError):
            self.engine(runner).paint(self.request, 1)

    def test_timeout_is_retryable(self):
        def runner(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd, codex.TIMEOUT)

        with self.assertRaises(RetryablePaintError):
            self.engine(runner).paint(self.request, 1)

    def test_login_status_wants_chatgpt(self):
        def chatgpt(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "Logged in using ChatGPT", "")

        def api_key(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, "Logged in using an API key", "")

        self.assertTrue(codex.login_status(["codex"], runner=chatgpt)[0])
        self.assertFalse(codex.login_status(["codex"], runner=api_key)[0])


def alive(pid: int) -> bool:
    """잠깐 기다리며 그 프로세스가 아직 도는지 본다 (좀비는 끝난 것으로 친다)"""
    for _ in range(30):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        stat = Path(f"/proc/{pid}/stat")
        if stat.exists() and stat.read_text().rsplit(")", 1)[-1].split()[0] == "Z":
            return False
        time.sleep(0.1)
    return True


class CodexEnvTest(HomeTestCase):
    def test_login_check_uses_the_same_env_as_drawing(self):
        seen = {}

        def runner(cmd, env=None, **kwargs):
            seen["env"] = env
            return subprocess.CompletedProcess(cmd, 0, "Logged in using ChatGPT", "")

        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-x"}):
            self.assertTrue(codex.login_status(["codex"], runner=runner)[0])
        self.assertNotIn("OPENAI_API_KEY", seen["env"])

    def test_codex_never_sees_the_secret_keys(self):
        folder = make_story(images=False)
        data = story.load(folder)
        request = painter.request_for(data, data["pages"][0], folder)
        seen = {}

        def runner(cmd, input, cwd, env=None, **kwargs):
            seen["env"] = env
            Path(re.search(r"exact path: (.+)", input).group(1).strip()).write_bytes(png())
            return subprocess.CompletedProcess(cmd, 0, "DONE", "")

        keys = {"OPENAI_API_KEY": "sk-x", "FAL_KEY": "f", "FISH_AUDIO_API_KEY": "a", "FISH_VOICE_ID": "v"}
        with mock.patch.dict(os.environ, keys):
            engine = codex.CodexEngine(cmd=["codex"], runner=runner)
            engine.paint(request, 1)
            engine.close()
        self.assertFalse(set(keys) & set(seen["env"]))
        self.assertIn("PATH", seen["env"])

    def test_leftover_folders_from_a_killed_run_are_swept(self):
        parent = self.tmp / "tmp"
        parent.mkdir()
        dead = parent / "storybook-codex-dead"
        dead.mkdir()
        (dead / "child.jpg").write_bytes(b"photo")
        live = parent / "storybook-codex-live"
        live.mkdir()
        other = parent / "storybook-static-old"  # 같은 이름을 쓰는 다른 프로그램의 폴더는 그대로 둔다
        other.mkdir()
        old = time.time() - 3 * 3600
        os.utime(dead, (old, old))
        os.utime(other, (old, old))
        with mock.patch("tempfile.tempdir", str(parent)):
            engine = codex.CodexEngine(cmd=["codex"])
        self.assertFalse(dead.exists())
        self.assertTrue(live.exists())
        self.assertTrue(other.exists())
        self.assertEqual(engine.dir.parent, parent)
        engine.close()


@unittest.skipIf(os.name == "nt", "프로세스 묶음 끄기는 리눅스·Mac에서 시험해요")
class CodexProcessTest(HomeTestCase):
    """가짜 Codex가 아래 프로세스를 하나 더 띄우고 오래 잔다. 끌 때 둘 다 꺼져야 한다."""
    SCRIPT = ("import subprocess, sys, time\n"
              "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
              "open('child.pid', 'w').write(str(child.pid))\n"
              "time.sleep(60)\n")

    def setUp(self):
        super().setUp()
        folder = make_story(images=False)
        data = story.load(folder)
        self.request = painter.request_for(data, data["pages"][0], folder)
        script = self.tmp / "fake_codex.py"
        script.write_text(self.SCRIPT, encoding="utf-8")
        self.engine = codex.CodexEngine(cmd=[sys.executable, str(script)])

    def wait_for_child(self) -> int:
        marker = self.engine.dir / "child.pid"
        for _ in range(100):
            if marker.exists() and marker.read_text():
                return int(marker.read_text())
            time.sleep(0.1)
        self.fail("가짜 Codex가 뜨지 않았어요")

    def test_timeout_stops_codex_and_everything_it_started(self):
        with mock.patch.object(codex, "TIMEOUT", 2):
            with self.assertRaises(RetryablePaintError):
                self.engine.paint(self.request, 1)
        pid = int((self.engine.dir / "child.pid").read_text())
        self.engine.close()
        self.assertFalse(alive(pid))

    def test_close_stops_codex_that_is_still_drawing(self):
        errors = []

        def run():
            try:
                self.engine.paint(self.request, 1)
            except PaintError as e:
                errors.append(e)

        worker = threading.Thread(target=run)
        worker.start()
        pid = self.wait_for_child()
        self.engine.close()
        worker.join(10)
        self.assertFalse(worker.is_alive())
        self.assertFalse(alive(pid))
        self.assertFalse(self.engine.dir.exists())
