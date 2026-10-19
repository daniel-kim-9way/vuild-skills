import json
import re

from storybook import pages, paths, story, voice
from tests.helpers import HomeTestCase, make_story


def payload(html: str) -> dict:
    raw = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1)
    return json.loads(raw)


class PagesTest(HomeTestCase):
    def test_draft_page(self):
        folder = make_story(images=False)
        path = pages.build("draft", folder)
        self.assertEqual(path, folder / "1-글확인.html")
        html = path.read_text(encoding="utf-8")
        data = payload(html)
        self.assertEqual((data["kind"], data["screen"], data["folder"]), ("draft", "글 확인", str(folder)))
        self.assertEqual([p["label"] for p in data["pages"]][:2], ["표지", "1쪽"])
        self.assertEqual(data["cast"][1], {"name": "뭉치", "kind": "곰 인형", "photo": "사진/toy1.jpg"})
        self.assertIn('id="copy"', html)
        self.assertIn('href="../../.assets/common.css"', html)
        for name in ("common.css", "common.js", "Jua-Regular.ttf"):
            self.assertTrue((paths.home() / ".assets" / name).exists(), name)

    def test_text_cannot_break_out_of_script(self):
        folder = make_story(images=False)
        story.edit(folder, 1, text='뭉치가 "</script><img src=x onerror=alert(1)>" 하고 외쳤어요. 서준이는 깜짝 놀라 웃었어요.')
        html = pages.build("draft", folder).read_text(encoding="utf-8")
        self.assertEqual(html.count("</script>"), 2)  # 데이터 칸과 common.js 칸을 닫는 것뿐
        self.assertIn("onerror", payload(html)["pages"][1]["text"])

    def test_art_page_versions_images_and_shows_notes(self):
        folder = make_story(images=True)
        data = story.load(folder)
        data["pages"][4]["redraw_note"] = "손가락이 세 개여야 해요"
        story.save(folder, data)
        shown = payload(pages.build("art", folder).read_text(encoding="utf-8"))
        self.assertEqual(shown["pages"][4]["note"], "손가락이 세 개여야 해요")
        self.assertRegex(shown["pages"][1]["image"], r"^그림/p1\.jpg\?v=\d+$")

    def test_book_page_links_video_when_present(self):
        folder = make_story(images=True)
        self.assertIsNone(payload(pages.build("book", folder).read_text(encoding="utf-8"))["video"])
        story.video_path(folder, story.load(folder)).write_bytes(b"fake")
        shown = payload(pages.build("book", folder).read_text(encoding="utf-8"))
        self.assertEqual(shown["video"], "서준이와 뭉치의 밤 소리 탐험.mp4")

    def test_voice_page(self):
        files = []
        for voice_id, name in voice.VOICES.items():
            f = paths.home() / ".assets" / "voices" / f"{voice_id}.mp3"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b"x")
            files.append({"id": voice_id, "label": name, "file": f})
        path = pages.voice_page(files)
        self.assertEqual(path, paths.home() / "목소리고르기.html")
        html = path.read_text(encoding="utf-8")
        self.assertIn('href=".assets/common.css"', html)
        self.assertEqual(payload(html)["voices"][0]["file"], ".assets/voices/ko-KR-SunHiNeural.mp3")

    def test_nothing_loads_from_the_internet(self):
        for name in ("page.html", "common.js", "common.css"):
            self.assertNotRegex((pages.TEMPLATES / name).read_text(encoding="utf-8"), r"https?://", name)


class ScriptEscapeTest(HomeTestCase):
    def test_comment_marker_cannot_swallow_the_page_script(self):
        # <!--<script>가 데이터 칸에 있으면 브라우저가 뒤의 </script>를 못 보고 common.js까지 삼킨다
        folder = make_story(images=False)
        story.edit(folder, 1, text="뭉치가 <!--<script> 하고 외쳤어요. 서준이는 깜짝 놀라 웃었어요.")
        html = pages.build("draft", folder).read_text(encoding="utf-8")
        self.assertNotIn("<!--", html)
        self.assertEqual(html.count("<script"), 2)
        self.assertIn("<!--<script>", payload(html)["pages"][1]["text"])
