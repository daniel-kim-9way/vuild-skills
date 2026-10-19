import datetime

from storybook import paths, people, story
from tests.helpers import HomeTestCase, draft, make_story, save_people

DAY = datetime.date(2026, 10, 16)


class StoryTest(HomeTestCase):
    def setUp(self):
        super().setUp()
        save_people()

    def test_create_makes_folder_with_photos(self):
        folder = story.create(draft(), today=DAY)
        self.assertEqual(folder.name, "2026-10-16-서준이와-뭉치의-밤-소리-탐험")
        data = story.load(folder)
        self.assertEqual(data["pages"][0]["text"], data["title"])
        self.assertEqual(data["created"], "2026-10-16")
        self.assertEqual([c["photo"] for c in data["cast"]], ["사진/child.jpg", "사진/toy1.jpg"])
        self.assertTrue((folder / "사진" / "toy1.jpg").exists())
        self.assertTrue(all(p["image"] is None for p in data["pages"]))
        self.assertIsInstance(data["seed"], int)
        self.assertEqual(people.get_person("뭉치")["look_en"], "a small brown teddy bear with a red ribbon")

    def test_same_title_twice_gets_a_new_folder(self):
        first = story.create(draft(), today=DAY)
        second = story.create(draft(), today=DAY)
        self.assertEqual(second.name, first.name + "-2")

    def test_title_with_forbidden_letters(self):
        folder = story.create(draft(title='별/달: "꿈"?'), today=DAY)
        self.assertEqual(folder.name, "2026-10-16-별달-꿈")

    def test_check_catches_common_mistakes(self):
        bad = draft()
        bad["pages"] = bad["pages"][:8]
        bad["pages"][2]["prompt_en"] = "서준이가 웃어요"
        bad["pages"][3]["cast"] = ["toy2"]
        with self.assertRaises(story.StoryError) as caught:
            story.create(bad)
        text = str(caught.exception)
        self.assertIn("모두 9쪽", text)
        self.assertIn("영어로만", text)
        self.assertIn("toy2", text)

    def test_missing_person_is_named(self):
        bad = draft()
        bad["cast"][1]["name"] = "토토"
        with self.assertRaises(story.StoryError) as caught:
            story.create(bad)
        self.assertIn("토토", str(caught.exception))

    def test_short_text_is_a_warning_not_an_error(self):
        data = story.normalize(draft())
        data["pages"][2]["text"] = "짧아요."
        errors, warnings = story.check(data)
        self.assertEqual(errors, [])
        self.assertTrue(any("2쪽 글이 4자예요" in w for w in warnings))

    def test_edit_text_drops_old_voices(self):
        folder = story.create(draft())
        data = story.load(folder)
        data["pages"][2]["voices"] = ["목소리/p2-0.mp3"]
        data["pages"][2]["zones"] = ["top"]
        story.save(folder, data)
        page = story.edit(folder, 2, text="뭉치가 살금살금 다가가서 창문 밖을 내다보았어요. 바람이 나뭇잎을 흔들고 있었어요.")
        self.assertEqual((page["voices"], page["zones"]), ([], []))

    def test_edit_prompt_drops_image_and_keeps_note(self):
        folder = make_story(images=True)
        image = folder / "그림" / "p3.jpg"
        self.assertTrue(image.exists())
        page = story.edit(folder, 3, prompt_en="[child] holding up exactly THREE fingers.", note="손가락이 세 개여야 해요")
        self.assertIsNone(page["image"])
        self.assertFalse(image.exists())
        self.assertEqual(page["redraw_note"], "손가락이 세 개여야 해요")

    def test_edit_cover_text_changes_title(self):
        folder = story.create(draft())
        story.edit(folder, 0, text="서준이와 뭉치의 별빛 산책")
        self.assertEqual(story.load(folder)["title"], "서준이와 뭉치의 별빛 산책")

    def test_edit_rejects_breaking_changes(self):
        folder = story.create(draft())
        with self.assertRaises(story.StoryError):
            story.edit(folder, 4, prompt_en="서준이가 달려요")
        with self.assertRaises(story.StoryError):
            story.edit(folder, 12, text="없는 쪽")

    def test_delete_only_story_folders(self):
        folder = story.create(draft())
        with self.assertRaises(story.StoryError):
            story.delete(paths.people_dir())
        story.delete(folder)
        self.assertFalse(folder.exists())

    def test_list_and_summary(self):
        folder = make_story(images=True)
        self.assertEqual(story.all_stories(), [folder])
        self.assertIn("그림 9/9", story.summary(folder))
        self.assertIn("MP4 없음", story.summary(folder))

    def test_examples_and_themes(self):
        self.assertEqual(len(story.themes()), 12)
        text = story.examples("courage")
        self.assertIn("밤 소리 탐험", text)
        self.assertIn("1쪽:", text)
        with self.assertRaises(story.StoryError):
            story.examples("nope")
