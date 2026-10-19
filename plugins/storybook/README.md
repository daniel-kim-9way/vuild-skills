# 동화 공방 (storybook)

아이와 아이가 아끼는 인형 사진으로 그림 동화를 만들어 주는 Claude Code 플러그인이에요.
Claude가 글을 쓰고, 고른 엔진이 그림을 그리고, 목소리가 읽어 주는 MP4까지 만들어요.

## 설치

Claude Code에서:
```
/plugin marketplace add daniel-kim-9way/vuild-skills
/plugin install storybook@vuild
/reload-plugins
```
처음이면 `/storybook:setup`부터 해요. 그다음부터는 «동화 만들어줘»라고 하거나 `/storybook:make`.

## 필요한 것

| 무엇 | 설명 |
|---|---|
| Claude Code | 글을 써요 |
| Python 3.9 이상, ffmpeg | setup이 확인하고 설치 명령을 알려 줘요 |
| 그림 | Codex(ChatGPT 유료 구독) 또는 fal.ai 키 중 하나 |
| 목소리 | 없어도 돼요(무료 기본 목소리). Fish Audio 키가 있으면 그 목소리로 읽어요 |

## 돈과 시간 (한 편: 표지 + 8쪽)

| 엔진 | 돈 | 시간 |
|---|---|---|
| Codex | 추가 비용 없음(ChatGPT 구독 사용량에서 빠져요) | 그림 15분쯤 |
| fal.ai | 700~1,100원쯤 | 그림 3분쯤 |
| 목소리·MP4 | 무료 | 2분쯤 |

## 사진은 어디로 가나요

- 사진은 내 PC의 `~/동화공방/`에만 저장해요. 긴 변 1000px로 줄이고 촬영 위치 같은 정보를 지워요.
- 글을 쓰는 Claude(Anthropic)가 사진을 봐요.
- 그림 엔진(Codex면 OpenAI, 아니면 fal.ai)이 사진을 받아 그림을 그려요.
- 목소리 엔진에는 글만 가요.

## 파일은 어디에 생기나요

```
~/동화공방/
  settings.json  .env(비밀값)  .venv/  .assets/
  인물/<이름>/photo.jpg
  동화/<날짜>-<제목>/  story.json  그림/  목소리/  1-글확인.html  2-그림확인.html  동화.html  <제목>.mp4
```
`STORYBOOK_HOME` 환경 변수로 위치를 바꿀 수 있어요.

## 문제가 생기면

| 증상 | 해결 |
|---|---|
| ffmpeg가 없어요 | Mac `brew install ffmpeg`, Windows `winget install Gyan.FFmpeg`(설치한 뒤 Claude Code를 다시 켜요), Ubuntu `sudo apt install -y ffmpeg` |
| 패키지를 깔지 못했어요 (Ubuntu) | `sudo apt install -y python3-venv` 뒤에 다시 |
| Codex 사용량 한도 | 한도가 풀린 뒤 «이어서 그려 줘» |
| 브라우저가 안 열려요 | 출력에 나온 HTML 파일을 직접 열어요 |
| 복사가 안 돼요 | 화면에 뜬 글 상자에서 Ctrl+C(Mac은 ⌘C) |
| Mac에서 fal.ai·Fish Audio에 연결하지 못해요 | python.org에서 받은 Python이면 `/Applications/Python 3.x/Install Certificates.command`를 한 번 실행해요 |
| MP4가 다른 프로그램에서 열려 있어요 | 동영상 플레이어를 닫고 다시 만들어요 |

## 출처와 라이선스

- 글쓰기 규칙과 예시 동화 32편은 «동화 공방» 앱에서 가져왔어요. 옛이야기(이솝 우화, 전래동화, 그림 형제, 안데르센, 『벨벳 토끼』)는 저작권이 끝난 것만 줄거리 구조를 빌렸고, 나머지는 새로 썼어요.
- 글꼴: 주아체(Jua), SIL Open Font License 1.1 (`assets/OFL-Jua.txt`)
- 음악: 저작권이 끝난 곡(브람스 자장가, 반짝반짝 작은 별)과 새로 만든 선율을 코드로 합성한 소리
- 이 플러그인: MIT (`LICENSE`)

## 개발

```bash
uv venv .venv --python python3 && uv pip install --python .venv/bin/python pillow pillow-heif edge-tts pyyaml
.venv/bin/python -m unittest discover -s tests -t . -v
```
`reference/writing.md`, `reference/patterns.yml`, 그림 화풍 문장(`painter.py`의 STYLE·RULES)은 동화 공방 앱과 같아야 해요. 한쪽을 고치면 다른 쪽도 고쳐요.
