from pathlib import Path
from unittest import mock

from PIL import Image

from storybook import paths, people
from tests.helpers import HomeTestCase, make_image


class CleanPhotoTest(HomeTestCase):
    def src(self, name: str) -> Path:
        path = self.tmp / "src" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def test_shrinks_and_drops_exif(self):
        src = self.src("big.jpg")
        exif = Image.Exif()
        exif[0x010F] = "TestCam"  # 찍은 기기 이름
        Image.new("RGB", (3000, 2000), (10, 20, 30)).save(src, "JPEG", exif=exif)
        with Image.open(people.clean_photo(src, self.tmp / "out.jpg")) as image:
            self.assertEqual(image.size, (1000, 667))
            self.assertEqual(len(image.getexif()), 0)

    def test_turns_photo_upright(self):
        src = self.src("turned.jpg")
        exif = Image.Exif()
        exif[0x0112] = 6  # 휴대폰을 돌려 찍은 사진
        Image.new("RGB", (400, 200), "white").save(src, "JPEG", exif=exif)
        with Image.open(people.clean_photo(src, self.tmp / "out.jpg")) as image:
            self.assertEqual(image.size, (200, 400))

    def test_transparent_png_gets_white_background(self):
        src = self.src("toy.png")
        Image.new("RGBA", (50, 50), (0, 0, 0, 0)).save(src)
        with Image.open(people.clean_photo(src, self.tmp / "out.jpg")) as image:
            self.assertGreater(min(image.getpixel((25, 25))), 240)

    def test_heic_is_read(self):
        import pillow_heif
        src = self.src("phone.heic")
        try:
            pillow_heif.from_pillow(Image.new("RGB", (64, 48), (200, 100, 50))).save(str(src))
        except Exception as e:  # HEIC 저장 기능이 없는 빌드
            self.skipTest(f"HEIC를 만들 수 없어요: {e}")
        with Image.open(people.clean_photo(src, self.tmp / "out.jpg")) as image:
            self.assertEqual(image.size, (64, 48))

    def test_not_a_photo(self):
        src = self.src("note.txt")
        src.write_text("hello")
        with self.assertRaises(people.PersonError):
            people.clean_photo(src, self.tmp / "out.jpg")


class SavedPeopleTest(HomeTestCase):
    def setUp(self):
        super().setUp()
        self.photo = make_image(self.tmp / "src" / "a.jpg")

    def test_save_list_get_remove(self):
        people.save_person("서준", "child", self.photo, age=4)
        people.save_person("뭉치", "toy", self.photo)
        self.assertEqual(sorted(p["name"] for p in people.list_people()), ["뭉치", "서준"])
        child = people.get_person("서준")
        self.assertEqual((child["role"], child["age"], child["kind_ko"]), ("child", 4, "아이"))
        self.assertTrue(Path(child["photo"]).exists())
        people.remove_person("뭉치")
        with self.assertRaises(people.PersonError):
            people.get_person("뭉치")

    def test_same_name_replaces_photo_and_forgets_look(self):
        people.save_person("뭉치", "toy", self.photo)
        people.remember_looks([{"name": "뭉치", "look_en": "a brown bear", "kind_ko": "곰 인형"}])
        self.assertEqual(people.get_person("뭉치")["look_en"], "a brown bear")
        self.assertEqual(people.get_person("뭉치")["kind_ko"], "곰 인형")
        people.save_person("뭉치", "toy", make_image(self.tmp / "src" / "b.jpg", color=(0, 0, 255)))
        again = people.get_person("뭉치")
        self.assertEqual(again["look_en"], "")
        with Image.open(again["photo"]) as image:
            self.assertGreater(image.getpixel((5, 5))[2], 200)

    def test_bad_role_and_empty_name(self):
        with self.assertRaises(people.PersonError):
            people.save_person("", "child", self.photo)
        with self.assertRaises(people.PersonError):
            people.save_person("서준", "parent", self.photo)

    def test_name_with_slash_stays_inside_people_folder(self):
        people.save_person("별/달", "toy", self.photo)
        self.assertEqual(people.get_person("별/달")["name"], "별/달")
        self.assertTrue(all(p.parent == paths.people_dir() for p in paths.people_dir().iterdir()))


class HugePhotoTest(HomeTestCase):
    def test_photo_bigger_than_pillows_default_limit_is_taken(self):
        # 2억 화소 휴대폰 사진은 Pillow 기본 한도(약 1억 8천만 화소)를 넘는다. 기본 한도를 작게 흉내 낸다.
        src = make_image(self.tmp / "big.jpg", size=(400, 400))
        with mock.patch.object(Image, "MAX_IMAGE_PIXELS", 1000):
            people.clean_photo(src, self.tmp / "out.jpg")
            self.assertEqual(Image.MAX_IMAGE_PIXELS, 1000)  # 끝나면 한도를 되돌린다
        self.assertTrue((self.tmp / "out.jpg").exists())

    def test_huge_photo_is_refused_in_korean(self):
        src = make_image(self.tmp / "big.jpg", size=(400, 400))
        with mock.patch.object(people, "PIXEL_LIMIT", 1000):
            with self.assertRaises(people.PersonError) as caught:
                people.clean_photo(src, self.tmp / "out.jpg")
        self.assertIn("너무 커요", str(caught.exception))

    def test_big_phone_photo_prints_no_english_warning(self):
        import warnings
        src = make_image(self.tmp / "big.jpg", size=(400, 400))  # 16만 화소: 한도(20만)의 절반은 넘고 한도 안
        with mock.patch.object(people, "PIXEL_LIMIT", 200_000), warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            people.clean_photo(src, self.tmp / "out.jpg")
        self.assertEqual([w for w in caught if issubclass(w.category, Image.DecompressionBombWarning)], [])
