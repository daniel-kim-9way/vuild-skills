---
name: install
description: "빌드(BUILD) 시작 전 개발 환경을 점검하고 빠진 것을 채운다. Ch.0에서 깐 git·Claude Code·Node.js·Ruby·Orca·GitHub CLI·Railway CLI가 정상인지 확인하고, AskUserQuestion으로 OS와 설치 항목을 선택 박스로 받아 고른 것만 하나씩 안내한다. Orca의 Claude Code에서 실행. Triggers: \"install\", \"/install\", \"설치\", \"환경 설치\", \"개발 환경 세팅\""
---

# /install — 개발 환경 점검 + 보완

빌드(BUILD)에 들어가기 전, 필요한 도구가 다 있는지 확인하고 **빠진 것만 하나씩** 채우도록 돕는다.

> - 모든 물음은 **`AskUserQuestion` 도구로 선택 박스**를 띄운다. **번호를 치라고 하지 않는다.**
> - 이 스킬은 **Orca 안의 Claude Code에서 도는 것을 전제**한다. 터미널 명령은 **사용자 승인을 받아 직접 실행해도 된다.** 다만 **GUI 설치(다운로드·설치 마법사)와 웹 계정 가입은 사용자가 직접** 한다 — 정확한 링크·순서를 주고 "됐으면 알려주세요"로 넘어간다.
> - ⚠️ **Ch.0-1에서 이미 계정 4개(claude.ai Pro · VUILD · GitHub · Railway)와 도구 7개(git · Claude Code · Node.js · Ruby · Orca · GitHub CLI · Railway CLI), 설정 3개(git config, gh auth login, railway login)를 끝냈다.** 이 스킬의 기본 임무는 재설치가 아니라 **점검**이다.

## 0. 먼저 점검 — 버전 확인

사용자에게 묻기 전에, 승인을 받아 아래를 실행하고 결과를 알려준다.

```
git --version
claude --version
node --version && npm --version
ruby --version
gh --version
railway --version
```

- 전부 버전이 나오고 Orca가 실행 중이면 → "환경 준비 끝"이라고 알리고 **2번(추가 항목)**으로 간다.
- 하나라도 없으면 → 그 항목만 1~3번 흐름으로 설치 안내한다. (전체 재설치 X)

## 1. OS 묻기 — `AskUserQuestion` (단일 선택)
선택지: **Windows** / **Windows + WSL** / **Mac** / **Linux**
- 비개발자 Windows는 WSL이 없는 경우가 많으니 **"Windows"(그냥)를 맨 위**에 둔다.
- 고른 OS에 맞춰 이후 명령을 준다 — Windows = winget·설치파일·PowerShell / WSL·Linux = apt·curl / Mac = brew·curl.

## 2. 설치 항목 묻기 — `AskUserQuestion` (multiSelect: true)
"이미 깔린 건 빼고 고르세요" 안내 후 **다중 선택**으로 받는다. 선택지:
- **git** — 버전 관리 (Ch.0-1에서 설치. 없으면 여기서)
- **Claude Code (CLI)** — 터미널 `claude` 명령 (Ch.0-1에서 설치. 없으면 여기서)
- **Orca** — 작업대 (Ch.0-1에서 설치. 없으면 여기서)
- **GitHub 계정** — 코드 백업·배포 (웹 가입)
- **GitHub CLI (gh)**
- **Railway 계정** — 배포용 (Ch.5)
- **Railway CLI**
- **Node.js** — `npm`(도구 설치 명령)이 여기 들어 있다. Railway CLI 등 대부분의 도구가 npm으로 깔리므로 **기본 필수**
- **Ruby** — Ch.4 빌드킷을 돌리는 엔진(3.2+). 웹서비스를 만들면 **필수**. 없으면 `bundle install`에서 막힌다

## 3. 고른 항목을 하나씩 안내
고른 순서대로 하나씩. 각 항목: **무엇·왜 한 줄 → (OS별) 명령/링크 → 확인 → "되면 알려주세요"**. 한 항목 끝나면 다음으로. 막히면 대안 1개 제시.

| 항목 | Windows(그냥) | WSL·Linux | Mac | 확인 |
|------|---------------|-----------|-----|------|
| git | `winget install --id Git.Git -e` | `sudo apt install -y git` | `xcode-select --install` | `git --version` (첫 사용 시 `git config --global user.name/user.email`) |
| Claude Code (CLI) | `winget install Anthropic.ClaudeCode` | `curl -fsSL https://claude.ai/install.sh \| bash` | `brew install --cask claude-code` | `claude --version` → `claude`로 로그인 (**Pro 이상 구독 필요**) |
| Orca | `winget install --id StablyAI.Orca` | AppImage·deb (onorca.dev/download) | `brew install --cask stablyai/orca/orca` | 실행 후 홈 폴더 접근 허용 + Claude 설정 가져오기 |
| Node.js | `winget install OpenJS.NodeJS.LTS` | `sudo apt install -y nodejs npm` | `brew install node` | `node --version` **+ `npm --version`** (둘 다 18+/정상). 안 나오면 **PATH 등록**(아래 참고) |
| Ruby | rubyinstaller.org 3.2+ (PATH 추가 체크) | `sudo apt install -y ruby-full` | `brew install ruby@3.3` | `ruby --version` (3.2 이상). 안 나오면 **터미널·Orca 재시작** |
| GitHub CLI (gh) | `winget install --id GitHub.cli -e` | `sudo apt install -y gh` | `brew install gh` | `gh --version` → `gh auth login` |
| Railway CLI | `npm i -g @railway/cli` | `npm i -g @railway/cli` | `brew install railway` | `railway --version` → `railway login` |

- **GitHub 계정 / Railway 계정**: 웹 가입(github.com / railway.com) — 링크 주고 "가입했으면 알려주세요".
- **Orca**: 설치 후 **Projects 옆 ＋ → 새 프로젝트 만들기(빈 폴더에서 시작) → 이름 입력 → 프로젝트 생성 → 열린 터미널에서 `claude`**까지 안내한다. (이미 있는 폴더는 ＋ → 폴더 찾아보기)
- **PATH 문제**: `node`/`npm`/`gh`/`railway`가 "명령을 찾을 수 없음"이면 재설치 전에 **PATH 등록**을 먼저 확인한다. 이 스킬은 Claude Code에서 도니 **직접 확인·수정해도 된다**(Windows=사용자 환경변수, Mac·Linux=`~/.zshrc`·`~/.bashrc`). 수정 후 **터미널 재시작 필수**임을 반드시 알린다.
- **Railway CLI**: `npm i -g @railway/cli` → `railway --version` → `railway login`(브라우저에서 GitHub 계정 승인).

## 4. 마무리
고른 항목을 ✓로 정리하고 안내한다:
> **환경 준비 끝 → `/setup`(Vuild 연결 + Rails 환경 마무리) → `/dashboard`로 빌드 시작.**

(Vuild MCP 연결과 Rails 환경(gem·DB)은 `/setup`이 하므로 여기서 다루지 않는다.
 단, **Ruby 런타임 자체**는 `/setup`이 깔기 전에 이미 있어야 편하므로 여기서 함께 점검한다 — Ch.0-2 단계 7에서 설치한다.)
