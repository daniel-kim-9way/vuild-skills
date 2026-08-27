# install — 도구별 설치 상세 (OS별 명령 모음)

SKILL.md의 진행 흐름에서 각 항목을 안내할 때 참고하는 상세 명령집이다.
사용자가 고른 항목만, 순서대로 하나씩 안내한다.

> ⚠️ git · Claude Code · Orca 3개는 **Ch.0-1에서 이미 설치**했다. 여기서는 없을 때만 다시 안내한다.

## 1) git — 버전 관리 (빌드 필수)
- Windows: `winget install --id Git.Git -e` (또는 https://git-scm.com/download/win)
- Mac: `xcode-select --install` (또는 https://git-scm.com)
- WSL/Linux: `sudo apt update && sudo apt install -y git`
- 확인: `git --version`
- 첫 사용이면: `git config --global user.name "이름"` / `git config --global user.email "메일"`

## 2) Claude Code (CLI) — 일하는 AI
- Windows: `winget install Anthropic.ClaudeCode`
- Mac: `brew install --cask claude-code`
- 공통(스크립트): `curl -fsSL https://claude.ai/install.sh | bash`
- 확인: `claude --version` → 첫 실행 `claude` → **Claude 계정 로그인**
- ⚠️ **Pro·Max·Team 구독 또는 Console 크레딧이 있어야 동작한다.** Free 플랜이면 "업그레이드 필요" 메시지가 뜬다.
- ⚠️ **Node.js는 필요 없다.** (예전 `npm install -g @anthropic-ai/claude-code` 방식은 이제 권장하지 않는다)

## 3) Orca — 작업대 (무료·MIT)
- Windows: `winget install --id StablyAI.Orca` (또는 onorca.dev/download의 설치파일)
- Mac: `brew install --cask stablyai/orca/orca` (또는 .dmg)
- Linux: AppImage 또는 .deb (onorca.dev/download)
- 첫 실행: **홈 폴더 접근 허용** + **기존 `~/.claude` 설정 가져오기**(2번 로그인을 물려받음)
- 사용 흐름: **Projects 옆 ＋ → 새 프로젝트 만들기(빈 폴더에서 시작) → 이름 → 프로젝트 생성 → 그 폴더에서 열린 터미널에 `claude`**
- ⚠️ **새 프로젝트 만들기**로 만들면 Orca가 폴더 생성 + git 초기화까지 해준다. 반면 **폴더 찾아보기**로 기존 폴더(압축만 푼 빌드킷 등)를 올릴 때는 git이 꺼져 있으면 먼저 `git init` + 커밋 1개가 필요하다.

## 4) Node.js — npm/npx (기본 필수)
- 공통: https://nodejs.org 의 **LTS** 설치
- WSL/Linux: `sudo apt install -y nodejs npm` (버전이 낮으면 nvm 또는 mise 권장)
- 확인: `node --version` **그리고 `npm --version`** (둘 다 나와야 함, node는 18 이상)
- 쓰이는 곳: Railway CLI(`npm i -g @railway/cli`), Vuild 학습 추적(`npx vuild-cli`) 등 대부분의 도구
- ⚠️ **PATH**: "명령을 찾을 수 없음"이면 설치 경로가 PATH에 없는 것. Windows는 설치 마법사의 "Add to PATH" 체크(기본값), Mac·Linux는 `~/.zshrc`/`~/.bashrc`에 경로 추가. **수정 후 터미널 재시작 필수**

## 4-1) Ruby — 빌드킷 엔진 (웹서비스 필수)
- Windows: https://rubyinstaller.org 에서 **3.2 이상** 설치 → 설치 마법사에서 PATH 추가 체크
- Mac: `brew install ruby@3.3` 또는 `mise install ruby@3.3`
- WSL/Linux: `sudo apt install -y ruby-full` (버전이 낮으면 mise/rbenv 권장)
- 확인: `ruby --version` (3.2 이상이어야 함)
- 쓰이는 곳: Ch.4 빌드킷의 `bundle install`·`bin/dev`. **없으면 그 자리에서 막힌다**
- ⚠️ OS마다 방법이 제각각이라 **직접 찾지 말고 "Ruby 3.2 이상 설치해줘, 내 OS에 맞게"로 AI에게 맡기는 게 빠르다.**
- ⚠️ Windows에서 설치 후 `ruby` 명령이 없다고 나오면 **터미널(및 Orca)을 껐다 켠다.**

## 5) GitHub 계정 — 코드 백업·배포
- https://github.com 가입 + **이메일 인증**까지
- "가입 끝났으면 알려주세요"로 다음 단계

## 6) GitHub CLI (gh) — 터미널에서 GitHub 연결
- Mac: `brew install gh`
- WSL/Linux: `sudo apt install -y gh`
- Windows: `winget install --id GitHub.cli -e`
- 연결: `gh auth login` / 확인: `gh --version`

## 7) Railway 계정 — 배포용 (Ch.5에서 사용)
- https://railway.com 에서 **GitHub로 가입** (지금 안 해도 됨)

## 8) Railway CLI — 배포 명령어
- Mac: `brew install railway`
- 공통: `npm i -g @railway/cli` (Node 필요)
- 로그인: `railway login` / 확인: `railway --version`

## 막혔을 때 (대안 1개씩)
- `winget`이 없다 → 각 도구의 공식 다운로드 페이지에서 설치 파일로 우회
- `brew` 실패 → 해당 도구의 공식 설치 페이지 또는 `curl` 스크립트로 우회
- `apt` 권한 오류 → `sudo` 확인, WSL 재시작
- `claude` 명령 없음 → **터미널을 껐다 켠 뒤** 재확인 (설치 직후엔 PATH가 반영 안 됨)
- Claude Code가 "업그레이드 필요"라고 함 → Free 플랜이다. claude.ai에서 Pro로 올린 뒤 `/login`
- Orca에서 폴더가 안 올라감 → 그 폴더에 `git init` + 빈 커밋이 있는지 확인

## 마무리
선택 항목을 ✓로 정리 → `/setup`(Vuild 연결 + Rails 마무리) → `/dashboard`로 빌드 시작.
