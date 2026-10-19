import json
import subprocess
from unittest import mock

from storybook import story, video
from tests.helpers import BODY, HomeTestCase, make_story


def quiet(_):
    pass


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class VideoTest(HomeTestCase):
    def test_build_makes_720p_mp4_named_after_title(self):
        folder = make_story(images=True)
        path = video.build(folder, progress=quiet)
        self.assertEqual(path, folder / "서준이와 뭉치의 밤 소리 탐험.mp4")
        info = probe(path)
        picture = next(s for s in info["streams"] if s["codec_type"] == "video")
        self.assertEqual((picture["width"], picture["height"]), (1280, 720))
        self.assertTrue(any(s["codec_type"] == "audio" for s in info["streams"]))
        # 목소리가 없으면 한 컷이 0.5 + max(3, 글자 수 × 0.13) + 1.2초, 끝 컷이 4초
        title = story.load(folder)["title"]
        expected = (0.5 + max(3.0, len(title) * 0.13) + 1.2) + 8 * (0.5 + max(3.0, len(BODY) * 0.13) + 1.2) + 4.0
        self.assertAlmostEqual(float(info["format"]["duration"]), expected, delta=1.0)
        self.assertTrue(all(len(p["zones"]) == 1 for p in story.load(folder)["pages"]))

    def test_music_off_and_unknown_music(self):
        folder = make_story(images=True)
        self.assertTrue(video.build(folder, music="off", progress=quiet).exists())
        self.assertEqual(story.load(folder)["music"], "off")
        with self.assertRaises(video.VideoError):
            video.build(folder, music="rock", progress=quiet)

    def test_missing_picture_is_named(self):
        folder = make_story(images=True)
        story.edit(folder, 3, redraw=True)
        with self.assertRaises(video.VideoError) as caught:
            video.build(folder, progress=quiet)
        self.assertIn("3쪽", str(caught.exception))

    def test_outlined_text_fits_and_wraps(self):
        image = video.outlined(BODY, 44, 400)
        stroke = max(round(44 * 0.13), 3)
        self.assertLessEqual(image.width, 400 + stroke * 6 + 2)
        self.assertGreater(image.height, 44 * 2)  # 두 줄 이상
        self.assertEqual(image.mode, "RGBA")

    def test_letters_the_font_lacks_are_swapped_or_dropped(self):
        self.assertEqual(video.drawable("서준·뭉치… ‘쉿’ — 「안녕」♪"), "서준, 뭉치... '쉿' - “안녕”")
        self.assertEqual(video.drawable("“귤이다!” 서준이가 외쳤어요."), "“귤이다!” 서준이가 외쳤어요.")

    def test_every_letter_on_the_cover_can_be_drawn(self):
        folder = make_story(images=True)
        line = video.cast_line(story.load(folder))
        self.assertEqual(line, "주인공: 서준, 뭉치")
        self.assertTrue(all(ch == " " or video.has_glyph(ch) for ch in line))

    def test_wrap_does_not_leave_one_word_alone(self):
        lines = video.wrap("하나 둘 셋 넷 다섯 여섯 일곱 여덟 아홉 열", 44, 500)
        self.assertGreater(len(lines), 1)
        self.assertGreater(len(lines[-1].split()), 1)

    def test_copy_to_downloads(self):
        downloads = self.tmp / "win" / "Downloads"
        downloads.mkdir(parents=True)
        movie = self.tmp / "a b.mp4"
        movie.write_bytes(b"movie")
        with mock.patch("storybook.paths.windows_home", return_value=self.tmp / "win"):
            self.assertEqual(video.copy_to_downloads(movie), downloads / "a b.mp4")
        with mock.patch("storybook.paths.windows_home", return_value=None):
            self.assertIsNone(video.copy_to_downloads(movie))


class VideoAfterEditTest(HomeTestCase):
    def test_new_title_leaves_one_mp4(self):
        folder = make_story(images=True)
        video.build(folder, music="off", progress=quiet)
        story.edit(folder, 0, text="서준이와 뭉치의 별 소리 탐험")
        path = video.build(folder, music="off", progress=quiet)
        self.assertEqual(path.name, "서준이와 뭉치의 별 소리 탐험.mp4")
        self.assertEqual(sorted(folder.glob("*.mp4")), [path])

    def test_temp_folder_with_apostrophe(self):
        odd = self.tmp / "o'brien"
        odd.mkdir()
        folder = make_story(images=True)
        with mock.patch("tempfile.tempdir", str(odd)):
            self.assertTrue(video.build(folder, music="off", progress=quiet).exists())

    def test_pages_without_voice_are_named(self):
        folder = make_story(images=True)
        notes = []
        video.build(folder, music="off", progress=notes.append)
        self.assertTrue(any("목소리 없이" in note and "표지" in note for note in notes), notes)

    def test_mp4_held_open_by_a_player(self):
        folder = make_story(images=True)
        with mock.patch("shutil.move", side_effect=PermissionError(13, "in use")):
            with self.assertRaises(video.VideoError) as caught:
                video.build(folder, music="off", progress=quiet)
        self.assertIn("열려", str(caught.exception))
