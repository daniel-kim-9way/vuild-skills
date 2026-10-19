import os
import re
import unittest
from pathlib import Path

from storybook import cli

ROOT = Path(__file__).resolve().parents[1]
DOCS = [*ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("reference/*.md"), ROOT / "README.md"]
PRIVATE_FILE = ROOT / "tests" / ".private-words"


def private_words() -> list[str]:
    """공개 저장소에 들어가면 안 되는 말(만든 사람의 아이·인형 이름, 개인 경로).
    그 말을 이 저장소에 적으면 그대로 공개되니, 만드는 사람 PC에만 둔다:
    STORYBOOK_PRIVATE_WORDS(쉼표로 구분)나 tests/.private-words(한 줄에 하나, git에 안 올라감)."""
    words = [w.strip() for w in os.environ.get("STORYBOOK_PRIVATE_WORDS", "").split(",") if w.strip()]
    if PRIVATE_FILE.exists():
        words += [line.strip() for line in PRIVATE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    return words


class DocsTest(unittest.TestCase):
    def test_every_sb_command_in_docs_exists(self):
        commands = set(cli.build_parser()._subparsers._group_actions[0].choices)
        for doc in DOCS:
            for name in re.findall(r"`sb ([a-z-]+)", doc.read_text(encoding="utf-8")):
                self.assertIn(name, commands, f"{doc.name}: sb {name}")

    def test_skill_front_matter(self):
        for name in ("setup", "make"):
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {name}\ndescription: "), name)

    def test_no_private_names(self):
        words = private_words()
        if not words:
            self.skipTest("검사할 말이 없어요 (tests/.private-words)")
        private = re.compile("|".join(map(re.escape, words)))
        for path in ROOT.rglob("*"):
            if ".venv" in path.parts or path.suffix not in {".md", ".py", ".js", ".css", ".html", ".json", ".yml"}:
                continue
            self.assertNotRegex(path.read_text(encoding="utf-8"), private, str(path))
