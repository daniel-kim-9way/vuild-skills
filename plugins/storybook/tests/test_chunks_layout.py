import unittest

from PIL import Image, ImageDraw

from storybook import chunks, layout
from tests.helpers import HomeTestCase


class ChunksTest(unittest.TestCase):
    def test_same_answers_as_the_app(self):
        self.assertEqual(chunks.split("“귤이다!” 서준이가 외쳤어요. 뭉치도 웃었어요."),
                         ["“귤이다!”", "서준이가 외쳤어요.", "뭉치도 웃었어요."])
        self.assertEqual(chunks.split("그런데 귤은 세 개뿐이었어요. 아! 어떡하지?"),
                         ["그런데 귤은 세 개뿐이었어요. 아!", "어떡하지?"])
        self.assertEqual(chunks.split("마침표 없는 글"), ["마침표 없는 글"])
        self.assertLessEqual(len(chunks.split("하나예요. 둘이에요. 셋이에요. 넷이에요. 다섯이에요. 여섯이에요.")),
                             chunks.MAX_CHUNKS)

    def test_cover_is_one_piece(self):
        self.assertEqual(chunks.for_page({"n": 0, "text": "밤 소리 탐험. 둘째 문장."}), ["밤 소리 탐험. 둘째 문장."])
        self.assertEqual(len(chunks.for_page({"n": 1, "text": "하나예요. 둘이에요."})), 2)


def striped(path, top_busy=False, bottom_busy=False):
    """가운데(인물이 있는 곳)에 세로 줄무늬가 있는 그림. 위·아래도 고를 수 있다."""
    image = Image.new("RGB", (400, 300), (250, 240, 220))
    draw = ImageDraw.Draw(image)

    def stripes(y0, y1):
        for x in range(0, 400, 16):
            draw.rectangle([x, y0, x + 7, y1], fill=(0, 0, 0))

    stripes(105, 195)
    if top_busy:
        stripes(0, 105)
    if bottom_busy:
        stripes(195, 300)
    image.save(path, "JPEG", quality=95)
    return path


class LayoutTest(HomeTestCase):
    def test_busy_middle_uses_calm_places_and_moves_each_sentence(self):
        path = striped(self.tmp / "a.jpg")
        zones = layout.zones(path, ["짧은 문장", "또 짧은 문장", "다시 짧은 문장"])
        self.assertIn(zones[0], ("top", "bottom"))
        for a, b in zip(zones, zones[1:]):
            self.assertFalse(layout.overlap(a, b), zones)

    def test_stays_on_calm_top_when_bottom_is_busy(self):
        path = striped(self.tmp / "b.jpg", bottom_busy=True)
        long = "아주 긴 문장이라서 모서리 칸에는 들어가지 않는 글이에요 정말로요"
        self.assertEqual(layout.zones(path, [long, long]), ["top", "top"])

    def test_overlap_rules(self):
        self.assertTrue(layout.overlap("top", "top-left"))
        self.assertFalse(layout.overlap("top-left", "top-right"))
        self.assertFalse(layout.overlap("top-left", "bottom-left"))
        self.assertTrue(layout.overlap("bottom", "bottom"))

    def test_broken_image_falls_back_to_top_and_bottom(self):
        bad = self.tmp / "bad.jpg"
        bad.write_bytes(b"not an image")
        self.assertEqual(layout.zones(bad, ["가", "나", "다"]), ["top", "bottom", "top"])
