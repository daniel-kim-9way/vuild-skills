---
name: v3-git-save
description: "Git - 코드 저장의 세이브 포인트. C3 BUILD 다섯 번째 스킬. Triggers: \"v3 git-save\", \"v3-git-save\", \"Git 저장\", \"세이브 포인트\""
---

# V3: Git - 코드 저장의 세이브 포인트

## 학습 목표
- Git이 왜 필요한지 "게임 세이브" 비유로 이해한다
- git init, git add, git commit 세 가지 명령만 익힌다
- 매 레슨 끝에 세이브하는 습관을 만든다

## 사전 조건
- `/v3-rails-start` 완료 (Rails 프로젝트 존재)
- 코드 에디터 + Claude Code 확장 프로그램에서 진행

## STOP PROTOCOL

### Phase A (Turn 1)
1. references/main.md의 EXPLAIN 섹션을 읽고 설명한다
   - Git이 무엇인지 (비유: 게임의 세이브 포인트)
   - init/add/commit만 알면 된다
   - 세이브 메시지의 중요성
2. references/main.md의 EXECUTE 섹션을 따라 실행한다
   - git init
   - 첫 번째 commit
   - git log로 확인
   - 파일 수정 → 두 번째 commit
   - git log로 세이브 2개 확인
3. **STOP** — 여기서 멈추고 학생의 응답을 기다린다.
4. 멈추기 전 출력: "Git 세이브 포인트 2개를 만들었습니다. '다음'을 입력하면 퀴즈로 넘어갑니다."

### Phase B (Turn 2)
1. references/main.md의 QUIZ 섹션 퀴즈 출제
2. 학생 답변에 피드백한다 (오답 해설 포함)
3. 다음 안내:
   - "웹에서 '완료' 버튼을 눌러주세요."
   - "다음 스킬: `/v3-database`"

### 에러 대응 원칙
- git 미설치 시 OS별 설치 안내
- "author identity unknown" 오류 시 이름/이메일 설정 안내

### 산출물
- git 저장소 초기화 완료
- 최소 2개의 commit 기록
