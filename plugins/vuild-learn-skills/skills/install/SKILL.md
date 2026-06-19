---
name: install
description: "빌드(BUILD) 시작 전 개발 환경을 한 번에 세팅. 무엇을 설치할지 먼저 고르게 하고(git·Node·Claude Code CLI·GitHub·gh·Railway·Railway CLI·에디터), 고른 것만 순서대로 하나씩 설치를 안내한다. Claude 앱의 Chat에서 실행. Triggers: \"install\", \"/install\", \"설치\", \"환경 설치\", \"개발 환경 세팅\""
---

# /install — 개발 환경 세팅 (하나씩 골라서 설치)

빌드(BUILD)에 들어가기 전, 필요한 도구를 **먼저 고르고 → 순서대로 하나씩** 설치하도록 돕는다.

> 이 스킬은 **Claude 앱의 Chat**에서 돈다(아직 터미널·에디터가 없어도 OK). 그래서 **명령을 대신 실행하지 않고**, 정확한 링크/명령어를 주고 **"다 됐으면 알려주세요"로 한 단계씩** 진행한다.

> ⚠️ 중요: **Claude Code(CLI)는 Claude 데스크탑 앱과 별개 패키지다.** 데스크탑 앱을 깔아도 터미널의 `claude` 명령은 안 생긴다 → **반드시 따로 설치**(아래 3번).

## 진행 방식

### 1. OS 확인
사용자 OS를 먼저 묻는다: **Mac / Windows(WSL) / Linux**. 우리 커리큘럼은 **WSL/터미널** 기준. 이후 모든 명령은 OS에 맞춰 준다.

### 2. 무엇을 설치할지 고르기 (선택 먼저!)
아래 목록을 보여주고, **이미 깔린 건 빼고 필요한 번호만** 받는다(여러 개 가능):

```
설치 도와드릴게요. 이미 있는 건 빼고, 필요한 번호만 알려주세요 (예: 1,2,3,5 또는 "전부"):
 1) git                — 버전 관리 (빌드 필수)
 2) Node.js            — npm/npx (Claude Code·gh·railway 설치에 사용)
 3) Claude Code (CLI)  — 터미널의 claude 명령  ※ 데스크탑 앱과 별개! 따로 설치해야 함
 4) GitHub 계정         — 코드 백업·배포 (웹 가입)
 5) GitHub CLI (gh)     — 터미널에서 GitHub 연결
 6) Railway 계정        — 배포용 (웹 가입, Ch.5에서 사용)
 7) Railway CLI         — 배포 명령어
 8) (선택) 에디터        — Antigravity + Claude Code 확장 (GUI로 작업하고 싶을 때)
```

선택을 받으면 **번호 순서대로 하나씩** 진행한다. 한 항목이 끝나고 사용자가 "완료/됐어"라고 하면 다음으로. **절대 여러 항목을 한 번에 시키지 않는다.**

### 3. 항목별 안내 (선택된 것만, 순서대로)

매 항목 형식: **무엇·왜 한 줄 → (OS별) 링크/명령어 → 확인 방법 → "다 됐으면 알려주세요"**.

- **git**
  - Mac: `xcode-select --install` (또는 https://git-scm.com)
  - Windows(WSL): WSL 안에서 `sudo apt update && sudo apt install -y git`
  - Linux: `sudo apt update && sudo apt install -y git`
  - 확인: `git --version`. 첫 사용이면 이름/이메일 설정(`git config --global user.name "이름"` / `user.email "메일"`).
- **Node.js**: https://nodejs.org 의 **LTS** 설치 (WSL이면 `sudo apt install -y nodejs npm`, 버전 낮으면 nvm/mise 권장). 확인 `node --version`(18 이상).
- **Claude Code (CLI)** — *데스크탑 앱을 깔았어도 따로 설치!*
  - WSL/Linux/Mac: `npm install -g @anthropic-ai/claude-code` (또는 네이티브 `curl -fsSL https://claude.ai/install.sh | bash`)
  - 확인: `claude --version`. 첫 실행 `claude` → **Claude.ai 계정으로 로그인**.
- **GitHub 계정**: https://github.com 가입 + **이메일 인증**까지. "가입 끝났으면 알려주세요."
- **GitHub CLI (gh)**: Mac `brew install gh` / WSL·Linux `sudo apt install -y gh` / Win `winget install --id GitHub.cli -e` → `gh auth login`. 확인 `gh --version`.
- **Railway 계정**: https://railway.com 에서 **GitHub로 가입**. (배포는 Ch.5 — 지금 안 해도 됨)
- **Railway CLI**: Mac `brew install railway` / 공통 `npm i -g @railway/cli`(Node 필요) → `railway login`. 확인 `railway --version`.
- **(선택) 에디터 — Antigravity + Claude Code 확장** (터미널 대신 GUI로 작업하고 싶을 때)
  1. https://antigravity.google → 설치 → Google 로그인
  2. 확장 마켓 → **Korean Language Pack** 설치
  3. 확장 마켓 → **Claude Code 확장** 설치 → Claude.ai 로그인
  - (Antigravity 터미널에서 `claude`를 쓰려면 위 3번 CLI도 필요)

### 4. 마무리
선택한 항목을 한 줄씩 ✓로 정리하고 다음을 안내:
```
환경 준비 끝! 이제 빌드킷 폴더에서 터미널(또는 에디터)을 열고
→ /setup (Vuild 연결 + Rails 환경 마무리) → /dashboard 로 빌드 시작하세요.
```

## 원칙
- **선택 먼저, 그다음 한 번에 하나씩.** 이미 깔린 건 다시 안 깐다("있어요" 하면 스킵).
- **Claude Code CLI는 데스크탑 앱과 별개**임을 분명히 한다(가장 자주 헷갈리는 지점).
- 막히면 그 항목의 **대안 설치법 1개** 제시(예: brew 실패 → 공식 설치 페이지).
- Chat에서 도는 스킬이라 **명령을 대신 실행하지 않는다** — 명령/링크를 주고, 사용자가 실행 후 결과를 알려주게 한다.
- Vuild MCP 연결과 Rails 환경(Ruby·Rails·DB)은 **`/setup`이** 하므로 여기서 다루지 않는다.
