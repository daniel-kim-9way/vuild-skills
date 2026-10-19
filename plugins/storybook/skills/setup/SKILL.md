---
name: setup
description: 동화 공방(storybook) 처음 준비와 엔진 고르기. Python·ffmpeg를 준비하고, 아이 사진이 어디로 가는지 알리고, 그림을 Codex와 fal.ai 중 무엇으로 그릴지, 목소리를 기본 목소리와 Fish Audio 중 무엇으로 할지 고르게 한다. "동화 공방 설치", "storybook setup", "그림 엔진 바꿔 줘", "목소리 바꿔 줘"에 쓴다. make 스킬이 준비가 안 됐다고 할 때도 쓴다.
---

# 동화 공방: 준비

## 먼저 알아 둘 것

- 이 스킬 폴더(스킬을 열 때 받은 Base directory)를 `SKILL_DIR`라고 해요. 명령은 이렇게 불러요.
  - Mac·리눅스·WSL: `python3 "SKILL_DIR/../../scripts/sb.py" <명령>`
  - Windows: `py -3 "SKILL_DIR\..\..\scripts\sb.py" <명령>`
  - 아래에서는 줄여서 `sb <명령>`이라고 적어요.
- 사람에게 하는 말은 한국어 입말로 짧게 해요.
- 비밀값(키)은 묻지도, 화면에 찍지도 않아요. `sb env open`으로 편집기를 열어 사람이 직접 넣게 해요. 사람이 채팅에 키를 붙여 넣으면 쓰지 말고, 그 키를 새로 만들라고 권해요.
- 참고 문서는 `SKILL_DIR/../../reference/`에 있어요.

## 1. 기본 도구

`python3 "SKILL_DIR/../../scripts/bootstrap.py"` (Windows: `py -3 …`)

- 처음에는 Python 패키지를 까느라 1~2분 걸린다고 먼저 말해요. Bash `timeout`은 600000(10분)으로 줘요. 기본 2분이면 중간에 꺼질 수 있어요.
- `✗ ffmpeg` → 출력에 나온 설치 명령을 알려 줘요. 명령에 `sudo`가 있으면 Claude가 비밀번호를 칠 수 없으니 사람이 직접 치게 해요: «`! sudo apt install -y ffmpeg`를 입력해 주세요».
- `✗ 패키지를 깔지 못했어요` → 출력에 나온 명령(예: `python3-venv`)을 깔게 하고 다시 돌려요.
- Python이 없으면: Mac `brew install python`, Windows `winget install Python.Python.3.12`.

## 2. 사진 안내

아래 글을 그대로 보여 주고 AskUserQuestion으로 «괜찮아요 / 그만할게요»를 받아요.

> 동화를 만들 때 아이·인형 사진은 이렇게 쓰여요.
> - 사진은 이 PC의 동화공방 폴더에만 저장해요. 긴 변 1000px로 줄이고 촬영 위치 같은 정보를 지워요.
> - 글을 쓰는 Claude(Anthropic)가 사진을 보고 생김새를 적어요.
> - 그림 엔진이 사진을 받아 그림을 그려요. Codex면 OpenAI, fal.ai면 fal이에요.
> - 목소리 엔진(Microsoft 또는 Fish Audio)에는 글만 가요.

«괜찮아요»면 `sb settings consent`. «그만할게요»면 여기서 멈춰요.

## 3. 그림 고르기

`sb codex check`가 0으로 끝나면 Codex 쪽에 «이 PC에 이미 있어요»와 «(Recommended)»를 붙여요. AskUserQuestion으로 물어요.

- **Codex**: ChatGPT 유료 구독, Codex 설치와 로그인. 추가 비용 없음. 9장에 15분쯤.
- **fal.ai**: 가입, 카드 등록, API 키. 한 편에 700~1,100원쯤. 3분쯤.

고르면 `reference/setup-image.md`에서 그 엔진 부분만 한 단계씩 안내해요. 한 단계 끝날 때마다 됐는지 물어요.
끝나면 `sb settings image codex` 또는 `sb settings image fal` → `sb draw-test`(Codex는 1~3분 걸려서 Bash `timeout`을 600000으로 줘요).
fal.ai면 시험 한 장에 100원 안팎이 든다고 먼저 말해요. 시험 그림이 열리면 잘 나왔는지 물어요.

## 4. 목소리 고르기

AskUserQuestion으로 물어요.

- **기본 목소리**: 무료, 키 없음. `sb voice-samples` → «브라우저에서 세 목소리를 들어 보고 고른 다음, 아래 버튼으로 복사해서 붙여 넣어 주세요». `[동화 공방 · 목소리 고르기] … 목소리(ko-KR-…)로 할게요`가 오면 `sb settings voice edge --name <그 ID>`.
- **Fish Audio**: `reference/setup-voice.md`대로 안내 → `sb env open` → 넣었다고 하면 `sb settings voice fish` → `sb fish check`.
  - 끝 코드가 3(비공개가 아님)일 때 내 목소리를 복제한 거라면, 비공개로 바꿀 때까지 다음으로 가지 않아요. 목소리 모음에서 고른 남의 목소리라면 괜찮아요.

## 5. 마무리

`sb doctor`가 0으로 끝나는지 봐요. 출력을 «준비 끝» 표로 짧게 보여 주고, 바로 동화를 만들지 물어요(→ make 스킬).

## 다시 고르기

- «그림 엔진 바꿔 줘» → 3단계만 해요.
- «목소리 바꿔 줘» → 4단계만 해요.
