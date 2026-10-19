import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from storybook import paths
from tests.helpers import HomeTestCase


class PathsTest(HomeTestCase):
    def test_home_follows_env(self):
        self.assertEqual(paths.home(), self.home)
        self.assertEqual(paths.people_dir(), self.home / "인물")
        self.assertEqual(paths.stories_dir(), self.home / "동화")

    def test_home_default_is_dongwha_gongbang(self):
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("STORYBOOK_HOME", None)
            self.assertEqual(paths.home(), Path.home() / "동화공방")

    def test_safe_name_keeps_korean_and_drops_forbidden(self):
        self.assertEqual(paths.safe_name("서준이와 뭉치의 밤 소리 탐험"), "서준이와 뭉치의 밤 소리 탐험")
        self.assertEqual(paths.safe_name('별/달: "꿈"?#1%'), "별달 꿈1")
        self.assertEqual(paths.safe_name("..."), "이름없음")
        self.assertEqual(len(paths.safe_name("가" * 100, 30)), 30)

    def test_local_path_strips_quotes_and_escaped_spaces(self):
        self.assertEqual(paths.local_path("'/tmp/a b.jpg'"), Path("/tmp/a b.jpg"))
        self.assertEqual(paths.local_path('"/tmp/c.jpg"'), Path("/tmp/c.jpg"))
        self.assertEqual(paths.local_path("/tmp/a\\ b.jpg"), Path("/tmp/a b.jpg"))

    def test_system_is_known(self):
        self.assertIn(paths.system(), {"mac", "windows", "wsl", "linux"})


class LocalPathTest(HomeTestCase):
    @unittest.skipIf(os.name == "nt", "윈도우 경로에서는 역슬래시를 그대로 둬요")
    def test_local_path_undoes_mac_terminal_escapes(self):
        self.assertEqual(paths.local_path("/Users/a/My\\ Photos/\\(1\\)\\ it\\'s.jpg"),
                         Path("/Users/a/My Photos/(1) it's.jpg"))

    def test_windows_home_reads_a_korean_user_name(self):
        # 한국어 윈도우의 cmd.exe는 /u를 주면 UTF-16으로 내보낸다. 안 주면 cp949라 한글 이름이 깨진다.
        calls = []

        def run(cmd, **kwargs):
            calls.append(cmd)
            if cmd[0] == "wslpath":
                return subprocess.CompletedProcess(cmd, 0, str(self.tmp) + "\n", "")
            return subprocess.CompletedProcess(cmd, 0, "C:\\Users\\홍길동\r\n".encode("utf-16-le"), b"")

        cmd_exe = self.tmp / "cmd.exe"
        cmd_exe.touch()
        with mock.patch("storybook.paths.system", return_value="wsl"), \
                mock.patch.object(paths, "WINDOWS_CMD", cmd_exe), mock.patch("subprocess.run", side_effect=run):
            self.assertEqual(paths.windows_home(), self.tmp)
        self.assertIn("/u", calls[0])
        self.assertEqual(calls[-1], ["wslpath", "-u", "C:\\Users\\홍길동"])
