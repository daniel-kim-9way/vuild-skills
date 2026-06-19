# install — 도구별 설치 상세 (OS별 명령 모음)

SKILL.md의 진행 흐름에서 각 항목을 안내할 때 참고하는 상세 명령집이다.
사용자가 고른 항목만, 순서대로 하나씩 안내한다.

## 1) git — 버전 관리 (빌드 필수)
- Mac: `xcode-select --install` (또는 https://git-scm.com)
- Windows(WSL): WSL 안에서 `sudo apt update && sudo apt install -y git`
- Linux: `sudo apt update && sudo apt install -y git`
- 확인: `git --version`
- 첫 사용이면: `git config --global user.name "이름"` / `git config --global user.email "메일"`

## 2) Node.js — npm/npx (Claude Code·gh·railway 설치에 사용)
- 공통: https://nodejs.org 의 **LTS** 설치
- WSL/Linux: `sudo apt install -y nodejs npm` (버전이 낮으면 nvm 또는 mise 권장)
- 확인: `node --version` (18 이상)

## 3) Claude Code (CLI) — ⚠️ 데스크탑 앱과 별개! 따로 설치
- 공통: `npm install -g @anthropic-ai/claude-code`
- 네이티브 대안: `curl -fsSL https://claude.ai/install.sh | bash`
- 확인: `claude --version` → 첫 실행 `claude` → **Claude.ai 계정 로그인**

## 4) GitHub 계정 — 코드 백업·배포
- https://github.com 가입 + **이메일 인증**까지
- "가입 끝났으면 알려주세요"로 다음 단계

## 5) GitHub CLI (gh) — 터미널에서 GitHub 연결
- Mac: `brew install gh`
- WSL/Linux: `sudo apt install -y gh`
- Windows: `winget install --id GitHub.cli -e`
- 연결: `gh auth login` / 확인: `gh --version`

## 6) Railway 계정 — 배포용 (Ch.5에서 사용)
- https://railway.com 에서 **GitHub로 가입** (지금 안 해도 됨)

## 7) Railway CLI — 배포 명령어
- Mac: `brew install railway`
- 공통: `npm i -g @railway/cli` (Node 필요)
- 로그인: `railway login` / 확인: `railway --version`

## 8) (선택) 에디터 — Antigravity + Claude Code 확장
1. https://antigravity.google → 설치 → Google 로그인
2. 확장 마켓 → **Korean Language Pack** 설치
3. 확장 마켓 → **Claude Code 확장** 설치 → Claude.ai 로그인
- (Antigravity 터미널에서 `claude`를 쓰려면 3번 CLI도 필요)

## 막혔을 때 (대안 1개씩)
- `brew` 실패 → 해당 도구의 공식 설치 페이지로 우회
- `apt` 권한 오류 → `sudo` 확인, WSL 재시작
- `claude` 명령 없음 → 데스크탑 앱이 아니라 **CLI(3번)**를 설치했는지 확인

## 마무리
선택 항목을 ✓로 정리 → `/setup`(Vuild 연결 + Rails 마무리) → `/dashboard`로 빌드 시작.
