r"""확인 화면을 실제 브라우저(Playwright)로 열어 본다. 윈도우 Python(Playwright가 깔린 쪽)으로 돌린다.

  WSL:  f=$(wslpath -w tests/browser_check.py); d=$(wslpath -w "<동화 폴더>"); (cd /mnt/c && cmd.exe /c py -3.13 "$f" "$d")
  그 밖: python browser_check.py "<동화 폴더>"

보는 것: 그림이 다 뜨는지, 가로로 넘치지 않는지(넓은 화면·휴대폰), 복사 버튼이 안내를 띄우는지,
복사될 글에 고친 내용과 동화 폴더가 들어가는지, 자바스크립트 오류가 없는지.
화면 사진은 동화 폴더의 _shots/ 에 남긴다.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

folder = Path(sys.argv[1])
home = folder.parent.parent
targets = [folder / name for name in ("1-글확인.html", "2-그림확인.html", "동화.html")] + [home / "목소리고르기.html"]
shots = folder / "_shots"
shots.mkdir(exist_ok=True)
problems = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    for width, height in ((1280, 900), (390, 844)):
        context = browser.new_context(viewport={"width": width, "height": height})
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        for target in targets:
            if not target.exists():
                continue
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(target.as_uri())
            page.wait_for_load_state("load")
            name = f"{target.stem}-{width}"
            if page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
                problems.append(f"{name}: 가로로 넘쳐요")
            broken = page.evaluate("[...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'))")
            if broken:
                problems.append(f"{name}: 안 뜬 그림 {broken}")
            if target.name == "1-글확인.html":
                page.locator("textarea").nth(1).fill("고친 문장이에요. 시험으로 고쳤어요.")
            page.click("#copy")
            page.wait_for_timeout(400)
            status = page.text_content("#copied") or ""
            message = page.evaluate("window.storybookMessage && window.storybookMessage()") or ""
            if not any(word in status for word in ("복사했어요", "Ctrl+C", "먼저 적어")):
                problems.append(f"{name}: 복사 안내가 안 떠요 ({status!r})")
            if target.name == "1-글확인.html" and "1쪽 고친 글" not in message:
                problems.append(f"{name}: 고친 글이 복사 글에 없어요")
            if target.name in ("1-글확인.html", "2-그림확인.html") and folder.name not in message:
                problems.append(f"{name}: 복사 글에 동화 폴더가 없어요")
            page.screenshot(path=str(shots / f"{name}.png"), full_page=True)
            problems += [f"{name}: {e}" for e in errors]
            page.close()
        context.close()
    browser.close()

print("\n".join(problems) or "문제 없음")
sys.exit(1 if problems else 0)
