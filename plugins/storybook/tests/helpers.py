"""테스트 도우미. 홈 폴더를 빈 임시 폴더로 바꿔 놓고 테스트한다."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image


class HomeTestCase(unittest.TestCase):
    """STORYBOOK_HOME을 «동화 공방»(띄어쓰기 포함) 임시 폴더로 바꾼다. 폴더는 만들지 않은 채로 둔다."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "동화 공방"
        self._old = os.environ.get("STORYBOOK_HOME")
        os.environ["STORYBOOK_HOME"] = str(self.home)

    def tearDown(self):
        if self._old is None:
            os.environ.pop("STORYBOOK_HOME", None)
        else:
            os.environ["STORYBOOK_HOME"] = self._old
        self._tmp.cleanup()


def make_image(path: Path, size=(800, 600), color=(200, 180, 160)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, "JPEG")
    return path


TITLE = "서준이와 뭉치의 밤 소리 탐험"
BODY = "서준이와 뭉치가 손을 꼭 잡고 깜깜한 마당으로 살금살금 천천히 걸어 나갔어요."


def draft(title: str = TITLE) -> dict:
    """Claude가 쓰는 초안과 같은 모양. 표지 + 본문 8쪽"""
    pages = [{"text": title, "cast": ["child", "toy1"],
              "prompt_en": "[child] and [toy1] smiling together under a starry sky."}]
    for n in range(1, 9):
        pages.append({"text": BODY, "cast": ["child", "toy1"],
                      "prompt_en": f"[child] and [toy1] walking in a moonlit garden, moment {n}."})
    return {
        "title": title, "lesson": "알고 나면 덜 무서워요.", "theme": "courage", "wish": "",
        "questions": ["밤에 들리는 소리 중에 뭐가 제일 궁금해?", "무서울 때 누가 옆에 있으면 좋아?"],
        "cast": [
            {"key": "child", "name": "서준", "age": 4, "kind_ko": "아이",
             "look_en": "a 4-year-old boy with short black hair and yellow pajamas"},
            {"key": "toy1", "name": "뭉치", "kind_ko": "곰 인형", "look_en": "a small brown teddy bear with a red ribbon"},
        ],
        "pages": pages,
    }


def save_people() -> None:
    from storybook import paths, people
    src = paths.home() / "_src"
    people.save_person("서준", "child", make_image(src / "child.jpg", color=(240, 200, 170)), age=4)
    people.save_person("뭉치", "toy", make_image(src / "toy.jpg", color=(140, 90, 50)))


def make_story(title: str = TITLE, images: bool = True) -> Path:
    """저장한 인물을 만들고 story.create로 동화 폴더를 만든다. images=True면 그림도 채운다."""
    from storybook import paths, story
    if not (paths.people_dir() / "서준").exists():
        save_people()
    folder = story.create(draft(title))
    if images:
        data = story.load(folder)
        for page in data["pages"]:
            name = "cover.jpg" if page["n"] == 0 else f"p{page['n']}.jpg"
            make_image(folder / "그림" / name, size=(1024, 768), color=(90 + page["n"] * 15, 140, 200))
            page["image"] = f"그림/{name}"
        story.save(folder, data)
    return folder
