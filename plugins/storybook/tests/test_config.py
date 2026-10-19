import os
import unittest
from unittest import mock

from storybook import config
from tests.helpers import HomeTestCase


class ConfigTest(HomeTestCase):
    def test_settings_merge_and_survive_reload(self):
        self.assertEqual(config.load_settings(), {})
        config.save_settings(image="codex")
        config.save_settings(voice={"engine": "edge", "voice": "ko-KR-SunHiNeural"})
        self.assertEqual(config.load_settings(),
                         {"image": "codex", "voice": {"engine": "edge", "voice": "ko-KR-SunHiNeural"}})

    def test_env_file_reads_values_and_skips_blanks(self):
        path = config.ensure_env_file()
        self.assertTrue(path.exists())
        # 메모장이 붙이는 BOM, 윈도우 줄바꿈, 따옴표도 견딘다
        path.write_text("\ufeff# 메모\nFAL_KEY=abc123\nFISH_AUDIO_API_KEY=\nFISH_VOICE_ID=\"v1\"\r\n", encoding="utf-8")
        self.assertEqual(config.read_env(), {"FAL_KEY": "abc123", "FISH_VOICE_ID": "v1"})

    def test_environment_wins_over_env_file(self):
        config.ensure_env_file().write_text("FAL_KEY=from-file\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"FAL_KEY": "from-env"}):
            self.assertEqual(config.secret("FAL_KEY"), "from-env")
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("FAL_KEY", None)
            self.assertEqual(config.secret("FAL_KEY"), "from-file")

    @unittest.skipIf(os.name == "nt", "윈도우는 권한 비트가 없어요")
    def test_env_file_is_private(self):
        self.assertEqual(config.ensure_env_file().stat().st_mode & 0o777, 0o600)

    def test_write_json_keeps_korean_and_leaves_no_temp_file(self):
        target = self.home / "a" / "b.json"
        config.write_json(target, {"이름": "서준"})
        self.assertIn("서준", target.read_text(encoding="utf-8"))
        self.assertEqual(config.read_json(target), {"이름": "서준"})
        self.assertEqual(list(target.parent.glob("*.tmp")), [])
