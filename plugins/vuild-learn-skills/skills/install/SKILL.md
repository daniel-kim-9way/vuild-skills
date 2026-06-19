---
name: install
description: "빌드(BUILD) 시작 전 개발 환경 세팅을 돕는다. AskUserQuestion으로 OS와 설치 항목을 선택 박스로 받고, 고른 것만 순서대로 하나씩 설치를 안내한다. Claude 앱 Chat에서 실행. Triggers: \"install\", \"/install\", \"설치\", \"환경 설치\", \"개발 환경 세팅\""
---

# /install — 개발 환경 세팅

빌드(BUILD)에 들어가기 전, 필요한 도구를 **선택해서 하나씩** 설치하도록 돕는다.

> - 모든 물음은 **`AskUserQuestion` 도구로 선택 박스**를 띄운다. **번호를 치라고 하지 않는다.**
> - Chat에서 도는 스킬이라 **명령을 대신 실행하지 않는다** — 정확한 명령/링크를 주고, 사용자가 실행한 뒤 결과를 알려주게 한다.
> - ⚠️ **Claude Code(CLI)는 Claude 데스크탑 앱과 별개 패키지다.** 앱을 깔아도 터미널 `claude` 명령은 안 생기니 따로 설치한다.

## 1. OS 묻기 — `AskUserQuestion` (단일 선택)
선택지: **Windows** / **Windows + WSL** / **Mac** / **Linux**
- 비개발자 Windows는 WSL이 없는 경우가 많으니 **"Windows"(그냥)를 맨 위**에 둔다.
- 고른 OS에 맞춰 이후 명령을 준다 — Windows = winget·설치파일·PowerShell / WSL·Linux = apt / Mac = brew.

## 2. 설치 항목 묻기 — `AskUserQuestion` (multiSelect: true)
"이미 깔린 건 빼고 고르세요" 안내 후 **다중 선택**으로 받는다. 선택지:
- **git** — 버전 관리 (빌드 필수)
- **Node.js** — npm/npx (Claude Code·gh·railway 설치에 사용)
- **Claude Code (CLI)** — 터미널 `claude` 명령 (데스크탑 앱과 별개·따로)
- **GitHub 계정** — 코드 백업·배포 (웹 가입)
- **GitHub CLI (gh)**
- **Railway 계정** — 배포용 (Ch.5)
- **Railway CLI**
- **에디터 (선택)** — Antigravity + Claude Code 확장

## 3. 고른 항목을 하나씩 안내
고른 순서대로 하나씩. 각 항목: **무엇·왜 한 줄 → (OS별) 명령/링크 → 확인 → "되면 알려주세요"**. 한 항목 끝나면 다음으로. 막히면 대안 1개 제시.

| 항목 | Windows(그냥) | WSL·Linux | Mac | 확인 |
|------|---------------|-----------|-----|------|
| git | `winget install --id Git.Git -e` | `sudo apt install -y git` | `xcode-select --install` | `git --version` (첫 사용 시 `git config --global user.name/user.email`) |
| Node.js | nodejs.org LTS(.msi) | `sudo apt install -y nodejs npm` | `brew install node` | `node --version` (18+) |
| Claude Code (CLI) | PowerShell `irm https://claude.ai/install.ps1 \| iex` | `curl -fsSL https://claude.ai/install.sh \| bash` | 〃(curl) | `claude --version` → `claude`로 로그인 |
| GitHub CLI (gh) | `winget install --id GitHub.cli -e` | `sudo apt install -y gh` | `brew install gh` | `gh --version` → `gh auth login` |
| Railway CLI | `npm i -g @railway/cli` | `npm i -g @railway/cli` | `brew install railway` | `railway --version` → `railway login` |

- **GitHub 계정 / Railway 계정**: 웹 가입(github.com / railway.com) — 링크 주고 "가입했으면 알려주세요".
- **에디터(Antigravity + Claude Code 확장)**: antigravity.google 설치 → 확장 마켓에서 Korean Language Pack + Claude Code 확장 설치.

## 4. 마무리
고른 항목을 ✓로 정리하고 안내한다:
> **환경 준비 끝 → `/setup`(Vuild 연결 + Rails 환경 마무리) → `/dashboard`로 빌드 시작.**

(Vuild MCP 연결과 Rails 환경(Ruby·Rails·DB)은 `/setup`이 하므로 여기서 다루지 않는다.)
