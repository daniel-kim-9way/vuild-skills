import io
import json
import urllib.error

from storybook import story, voice
from tests.helpers import HomeTestCase, make_story
from tests.test_fal import Response


class Recorder:
    """목소리 대신 글을 파일에 적는다"""

    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def edge(self, text, dest, voice_id=voice.DEFAULT_VOICE):
        self.calls.append(("edge", voice_id, text))
        dest.write_bytes(b"edge " + text.encode())

    def fish(self, text, dest, key, voice_id):
        if self.fail:
            raise voice.VoiceError("Fish Audio 오류 500")
        self.calls.append(("fish", voice_id, text))
        dest.write_bytes(b"fish " + text.encode())


def quiet(_):
    pass


class SpeakerTest(HomeTestCase):
    def test_edge_uses_chosen_voice(self):
        rec = Recorder()
        speaker = voice.Speaker({"engine": "edge", "voice": "ko-KR-InJoonNeural"}, edge=rec.edge, fish=rec.fish)
        speaker.say("안녕", self.tmp / "a.mp3")
        self.assertEqual(rec.calls, [("edge", "ko-KR-InJoonNeural", "안녕")])

    def test_fish_failure_falls_back_to_sunhi(self):
        rec = Recorder(fail=True)
        warnings = []
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "k", "FISH_VOICE_ID": "v"}):
            speaker = voice.Speaker({"engine": "fish"}, edge=rec.edge, fish=rec.fish, warn=warnings.append)
            speaker.say("안녕", self.tmp / "a.mp3")
        self.assertEqual(rec.calls, [("edge", voice.DEFAULT_VOICE, "안녕")])
        self.assertTrue(speaker.fell_back)
        self.assertTrue(warnings)


class NarrateTest(HomeTestCase):
    def test_makes_one_file_per_sentence_and_skips_finished_pages(self):
        folder = make_story(images=True)
        rec = Recorder()
        speaker = voice.Speaker({"engine": "edge", "voice": voice.DEFAULT_VOICE}, edge=rec.edge, fish=rec.fish)
        self.assertEqual(voice.narrate(folder, speaker, progress=quiet), 9)
        data = story.load(folder)
        self.assertEqual(data["pages"][3]["voices"], ["목소리/p3-0.mp3"])
        self.assertTrue((folder / "목소리" / "p3-0.mp3").exists())
        self.assertEqual(voice.narrate(folder, speaker, progress=quiet), 0)

    def test_changed_page_is_read_again(self):
        folder = make_story(images=True)
        rec = Recorder()
        speaker = voice.Speaker({"engine": "edge", "voice": voice.DEFAULT_VOICE}, edge=rec.edge, fish=rec.fish)
        voice.narrate(folder, speaker, progress=quiet)
        story.edit(folder, 4, text="뭉치가 귀를 쫑긋 세웠어요. 서준이는 숨을 죽이고 가만히 귀를 기울였어요.")
        rec.calls.clear()
        self.assertEqual(voice.narrate(folder, speaker, progress=quiet), 2)
        self.assertIn("뭉치가 귀를 쫑긋 세웠어요.", (folder / "목소리" / "p4-0.mp3").read_bytes().decode())

    def test_fish_failing_midway_rereads_earlier_pages_with_edge(self):
        folder = make_story(images=True)
        rec = Recorder()
        calls = {"n": 0}

        def flaky_fish(text, dest, key, voice_id):
            calls["n"] += 1
            if calls["n"] > 3:
                raise voice.VoiceError("Fish Audio 오류 503")
            rec.fish(text, dest, key, voice_id)

        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "k", "FISH_VOICE_ID": "v"}):
            speaker = voice.Speaker({"engine": "fish"}, edge=rec.edge, fish=flaky_fish, warn=quiet)
            voice.narrate(folder, speaker, progress=quiet)
        for n in range(9):
            self.assertTrue((folder / "목소리" / f"p{n}-0.mp3").read_bytes().startswith(b"edge "), n)


class FishHttpTest(HomeTestCase):
    def test_retries_busy_server_then_saves(self):
        answers = [urllib.error.HTTPError("u", 503, "busy", {}, io.BytesIO(b"")), Response(b"x" * 600)]
        sent = []

        def opener(req, timeout):
            sent.append(req)
            item = answers.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        dest = self.tmp / "f.mp3"
        voice.speak_fish("안녕", dest, "key", "vid", opener=opener, wait=lambda s: None)
        self.assertEqual(dest.read_bytes(), b"x" * 600)
        self.assertEqual(sent[0].get_header("Model"), voice.FISH_MODEL)
        self.assertEqual(json.loads(sent[0].data)["reference_id"], "vid")

    def test_visibility(self):
        def opener(req, timeout):
            return Response(json.dumps({"visibility": "private"}).encode())

        self.assertEqual(voice.fish_visibility("key", "vid", opener=opener), "private")


class SamplesTest(HomeTestCase):
    def test_three_samples_once(self):
        rec = Recorder()
        made = voice.samples(self.tmp / "voices", edge=rec.edge)
        self.assertEqual([m["id"] for m in made], list(voice.VOICES))
        voice.samples(self.tmp / "voices", edge=rec.edge)
        self.assertEqual(len(rec.calls), 3)


class VoiceChoiceTest(HomeTestCase):
    def test_changing_voice_rereads_every_page(self):
        folder = make_story(images=True)
        rec = Recorder()
        voice.narrate(folder, voice.Speaker({"engine": "edge", "voice": voice.DEFAULT_VOICE}, edge=rec.edge, fish=rec.fish),
                      progress=quiet)
        rec.calls.clear()
        other = voice.Speaker({"engine": "edge", "voice": "ko-KR-InJoonNeural"}, edge=rec.edge, fish=rec.fish)
        self.assertEqual(voice.narrate(folder, other, progress=quiet), 9)
        self.assertTrue(all(call[1] == "ko-KR-InJoonNeural" for call in rec.calls))

    def test_fish_failing_another_day_rereads_old_fish_pages(self):
        import os
        from unittest import mock
        folder = make_story(images=True)
        with mock.patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "k", "FISH_VOICE_ID": "v"}):
            good = Recorder()
            voice.narrate(folder, voice.Speaker({"engine": "fish"}, edge=good.edge, fish=good.fish, warn=quiet), progress=quiet)
            story.edit(folder, 4, text="뭉치가 귀를 쫑긋 세웠어요. 서준이는 숨을 죽이고 가만히 귀를 기울였어요.")
            bad = Recorder(fail=True)
            voice.narrate(folder, voice.Speaker({"engine": "fish"}, edge=bad.edge, fish=bad.fish, warn=quiet), progress=quiet)
        for page in story.load(folder)["pages"]:
            for rel in page["voices"]:
                self.assertTrue((folder / rel).read_bytes().startswith(b"edge "), rel)

    def test_new_fish_voice_id_rereads_every_page(self):
        import os
        from unittest import mock
        folder = make_story(images=True)
        rec = Recorder()
        with mock.patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "k", "FISH_VOICE_ID": "v1"}):
            voice.narrate(folder, voice.Speaker({"engine": "fish"}, edge=rec.edge, fish=rec.fish), progress=quiet)
        self.assertNotIn("v1", json.dumps(story.load(folder), ensure_ascii=False))  # 목소리 ID 값은 남기지 않는다
        with mock.patch.dict(os.environ, {"FISH_AUDIO_API_KEY": "k", "FISH_VOICE_ID": "v2"}):
            made = voice.narrate(folder, voice.Speaker({"engine": "fish"}, edge=rec.edge, fish=rec.fish), progress=quiet)
        self.assertEqual(made, 9)
