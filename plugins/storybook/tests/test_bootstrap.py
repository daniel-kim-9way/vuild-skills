import io
import subprocess
from contextlib import redirect_stdout
from unittest import mock

import bootstrap
from tests.helpers import HomeTestCase


class BootstrapTest(HomeTestCase):
    def test_hint_follows_system(self):
        with mock.patch("storybook.paths.system", return_value="mac"):
            self.assertEqual(bootstrap.hint("ffmpeg"), "brew install ffmpeg")
        with mock.patch("storybook.paths.system", return_value="wsl"):
            self.assertIn("apt install", bootstrap.hint("ffmpeg"))
            self.assertIn("python3-venv", bootstrap.hint("venv"))

    def test_missing_tools(self):
        with mock.patch("shutil.which", side_effect=lambda name: None if name == "ffprobe" else "/usr/bin/" + name):
            self.assertEqual(bootstrap.missing_tools(), ["ffprobe"])

    def test_check_only_reports_missing_venv_without_installing(self):
        out = io.StringIO()
        with mock.patch.object(bootstrap, "make_venv") as make, \
                mock.patch.object(bootstrap, "missing_tools", return_value=[]), redirect_stdout(out):
            code = bootstrap.main(["--check"])
        self.assertEqual(code, 2)
        make.assert_not_called()
        self.assertIn("아직 안 깔렸어요", out.getvalue())

    def test_install_failure_points_to_venv_package(self):
        out = io.StringIO()
        boom = subprocess.CalledProcessError(1, ["python3", "-m", "venv"])
        with mock.patch.object(bootstrap, "make_venv", side_effect=boom), \
                mock.patch.object(bootstrap, "missing_tools", return_value=[]), \
                mock.patch("storybook.paths.system", return_value="wsl"), redirect_stdout(out):
            code = bootstrap.main([])
        self.assertEqual(code, 2)
        self.assertIn("python3-venv", out.getvalue())

    def test_missing_ffmpeg_is_reported_with_install_command(self):
        out = io.StringIO()
        with mock.patch.object(bootstrap, "missing_tools", return_value=["ffmpeg", "ffprobe"]), \
                mock.patch.object(bootstrap, "venv_ready", return_value=True), \
                mock.patch("storybook.paths.system", return_value="mac"), redirect_stdout(out):
            code = bootstrap.main([])
        self.assertEqual(code, 2)
        self.assertIn("brew install ffmpeg", out.getvalue())
