import io
import os
import subprocess
import sys
import time

from PIL import Image

from storybook import painter, sheet, story
from storybook.painter import PaintError, RetryablePaintError
from tests.helpers import HomeTestCase, make_story


def png(size=(1536, 1024), color=(120, 160, 200)) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", size, color).save(out, "PNG")
    return out.getvalue()


class FakeEngine:
    """그림 대신 단색 PNG를 돌려준다. fail_at장을 그린 다음 장에서 사용량 한도처럼 멈출 수 있다."""
    name = "fake"

    def __init__(self, workers=1, fail_at=None, flaky=()):
        self.workers = workers
        self.fail_at = fail_at
        self.flaky = set(flaky)
        self.requests = []
        self.closed = False

    def paint(self, request, attempt):
        self.requests.append((request.n, attempt, request.style))
        if self.fail_at is not None and len({r[0] for r in self.requests}) > self.fail_at:
            raise PaintError("사용량 한도에 걸렸어요")
        if request.n in self.flaky and attempt == 1:
            raise RetryablePaintError("잠깐 실패")
        return png()

    def close(self):
        self.closed = True


def quiet(_):
    pass


class PainterTest(HomeTestCase):
    def test_request_replaces_markers_and_lists_references(self):
        folder = make_story(images=False)
        data = story.load(folder)
        page = data["pages"][2]
        page["prompt_en"] = "[child] hugs [toy1] while [toy2] watches."
        request = painter.request_for(data, page, folder)
        self.assertIn("the child from image 1 hugs the toy friend from image 2 while a friend watches.", request.prompt)
        self.assertIn("Image 2 is the reference photo of the toy friend: a small brown teddy bear", request.prompt)
        self.assertNotIn("[", request.prompt)
        self.assertNotIn(painter.COVER_NOTE, request.prompt)
        self.assertEqual(request.photos, [folder / "사진" / "child.jpg", folder / "사진" / "toy1.jpg"])
        self.assertIsNone(request.style)  # 표지가 아직 없다
        cover = painter.request_for(data, data["pages"][0], folder)
        self.assertIn(painter.COVER_NOTE, cover.prompt)

    def test_cover_first_then_style_reference(self):
        folder = make_story(images=False)
        engine = FakeEngine()
        self.assertEqual(painter.draw(folder, engine, progress=quiet), list(range(9)))
        self.assertEqual(engine.requests[0], (0, 1, None))
        cover = folder / "그림" / "cover.jpg"
        self.assertTrue(all(style == cover for _, _, style in engine.requests[1:]))
        self.assertEqual(story.load(folder)["pages"][4]["image"], "그림/p4.jpg")
        with Image.open(folder / "그림" / "p4.jpg") as image:
            self.assertEqual(image.size, (1365, 1024))
        self.assertTrue(engine.closed)

    def test_retry_then_success(self):
        folder = make_story(images=False)
        engine = FakeEngine(flaky={3})
        notes = []
        painter.draw(folder, engine, progress=notes.append)
        self.assertIn((3, 2, folder / "그림" / "cover.jpg"), engine.requests)
        self.assertTrue(any("3쪽 다시 그려요" in note for note in notes))

    def test_gives_up_after_three_tries(self):
        folder = make_story(images=False)

        class AlwaysFlaky(FakeEngine):
            def paint(self, request, attempt):
                raise RetryablePaintError("안전 검사에 걸렸어요")

        with self.assertRaises(PaintError) as caught:
            painter.draw(folder, AlwaysFlaky(), progress=quiet)
        self.assertIn("표지를 3번", str(caught.exception))

    def test_stop_keeps_finished_pages_and_resume_draws_the_rest(self):
        folder = make_story(images=False)
        with self.assertRaises(PaintError):
            painter.draw(folder, FakeEngine(fail_at=3), progress=quiet)
        drawn = [p["n"] for p in story.load(folder)["pages"] if p["image"]]
        self.assertEqual(drawn, [0, 1, 2])
        engine = FakeEngine()
        painter.draw(folder, engine, progress=quiet)
        self.assertEqual(sorted({r[0] for r in engine.requests}), [3, 4, 5, 6, 7, 8])

    def test_only_missing_pages_are_drawn_and_note_stays(self):
        folder = make_story(images=True)
        story.edit(folder, 5, redraw=True, note="고양이가 빠졌어요")
        engine = FakeEngine(workers=3)
        painter.draw(folder, engine, progress=quiet)
        self.assertEqual([r[0] for r in engine.requests], [5])
        self.assertEqual(story.load(folder)["pages"][5]["redraw_note"], "고양이가 빠졌어요")

    def test_only_argument_limits_pages(self):
        folder = make_story(images=False)
        engine = FakeEngine()
        self.assertEqual(painter.draw(folder, engine, only=[0, 2], progress=quiet), [0, 2])

    def test_sheet_puts_nine_pictures_on_one_image(self):
        folder = make_story(images=True)
        path = sheet.build(folder)
        self.assertEqual(path, folder / "그림" / "_모아보기.jpg")
        with Image.open(path) as image:
            self.assertEqual(image.size, (3 * 480 + 4 * 6, 3 * 360 + 4 * 6))


NEW_TEXT = "뭉치가 귀를 쫑긋 세웠어요. 서준이는 숨을 죽이고 가만히 귀를 기울였어요."


class DrawWhileEditingTest(HomeTestCase):
    def test_text_edited_while_drawing_is_kept(self):
        folder = make_story(images=False)

        class EditsMidway(FakeEngine):
            def paint(self, request, attempt):
                if request.n == 2:
                    story.edit(folder, 5, text=NEW_TEXT)
                return super().paint(request, attempt)

        painter.draw(folder, EditsMidway(), progress=quiet)
        page = story.load(folder)["pages"][5]
        self.assertEqual(page["text"], NEW_TEXT)
        self.assertEqual(page["image"], "그림/p5.jpg")

    def test_page_whose_prompt_changed_while_drawing_waits_for_the_next_draw(self):
        folder = make_story(images=False)

        class EditsSamePage(FakeEngine):
            def paint(self, request, attempt):
                if request.n == 4:
                    story.edit(folder, 4, prompt_en="[child] and [toy1] counting stars on the roof.")
                return super().paint(request, attempt)

        done = painter.draw(folder, EditsSamePage(), progress=quiet)
        self.assertNotIn(4, done)
        self.assertIsNone(story.load(folder)["pages"][4]["image"])
        self.assertEqual(painter.draw(folder, FakeEngine(), progress=quiet), [4])

    def test_picture_file_gone_means_draw_again(self):
        folder = make_story(images=True)
        (folder / "그림" / "p6.jpg").unlink()
        self.assertEqual([p["n"] for p in painter.pending(story.load(folder), folder=folder)], [6])
        self.assertEqual(painter.draw(folder, FakeEngine(), progress=quiet), [6])

    def test_second_draw_on_the_same_story_stops(self):
        folder = make_story(images=False)
        lock = folder / painter.LOCK_NAME
        lock.write_text(str(os.getpid()), encoding="utf-8")  # 살아 있는 프로세스가 그리는 중
        with self.assertRaises(PaintError) as caught:
            painter.draw(folder, FakeEngine(), progress=quiet)
        self.assertIn("그리는 중", str(caught.exception))
        old = time.time() - painter.LOCK_STALE - 60
        os.utime(lock, (old, old))
        self.assertEqual(len(painter.draw(folder, FakeEngine(), progress=quiet)), 9)
        self.assertFalse(lock.exists())

    def test_lock_left_by_a_dead_draw_is_taken_over(self):
        folder = make_story(images=False)
        gone = subprocess.Popen([sys.executable, "-c", "pass"])
        gone.wait()
        (folder / painter.LOCK_NAME).write_text(str(gone.pid), encoding="utf-8")
        self.assertEqual(len(painter.draw(folder, FakeEngine(), progress=quiet)), 9)

    def test_prompt_changed_before_its_turn_is_drawn_with_the_new_prompt(self):
        folder = make_story(images=False)

        class EditsLaterPage(FakeEngine):
            prompts = {}

            def paint(self, request, attempt):
                self.prompts[request.n] = request.prompt
                if request.n == 2:
                    story.edit(folder, 5, prompt_en="[child] and [toy1] counting stars on the roof.")
                return super().paint(request, attempt)

        engine = EditsLaterPage()
        self.assertIn(5, painter.draw(folder, engine, progress=quiet))
        self.assertIn("counting stars on the roof", engine.prompts[5])

    def test_stop_cancels_pages_waiting_in_line(self):
        # fal처럼 여러 장을 같이 그릴 때, 멈추면 줄 서 있던 쪽은 그리지 않는다 (돈이 나가지 않게)
        folder = make_story(images=False)

        class FailsOnPageOne(FakeEngine):
            def paint(self, request, attempt):
                self.requests.append((request.n, attempt, request.style))
                if request.n == 1:
                    raise PaintError("잔액이 모자라요")
                time.sleep(0.3)
                return png()

        engine = FailsOnPageOne(workers=2)
        with self.assertRaises(PaintError):
            painter.draw(folder, engine, progress=quiet)
        self.assertLessEqual(len({r[0] for r in engine.requests}), 5)
