---
name: v3-checkpoint
description: "체크포인트 - 내 서비스 동작 확인 + GitHub. C3 BUILD 열 번째 스킬. Triggers: \"v3 checkpoint\", \"v3-checkpoint\", \"C3 체크포인트\", \"서비스 점검\""
---

# V3: 체크포인트 - 내 서비스 동작 확인

## 학습 목표
- 내 서비스의 전체 기능을 체크리스트로 점검한다
- GitHub에 코드를 업로드하여 "클라우드 세이브"를 경험한다
- L1~L10 여정을 돌아보고 C4를 미리본다

## 사전 조건
- `/v3-feature-2` 완료 (두 번째 핵심 기능 구현)
- 코드 에디터 + Claude Code 확장 프로그램에서 진행

## STOP PROTOCOL

### Phase A (Turn 1)
1. references/main.md의 EXPLAIN 섹션을 읽고 설명한다
   - "시사회" 비유: 영화가 완성되면 시사회를 한다
   - GitHub = 클라우드 세이브 (내 컴퓨터가 고장나도 안전)
   - 지금까지의 여정 되돌아보기
2. references/main.md의 EXECUTE 섹션을 따라 실행한다
   - 전체 체크리스트 테스트
   - 문제 수정
   - GitHub 계정 생성/확인
   - git push (첫 업로드)
   - GitHub에서 확인
   - 여정 회고
3. **STOP** — 여기서 멈추고 학생의 응답을 기다린다.
4. 멈추기 전 출력: "C3 BUILD 챕터를 완료했습니다! '다음'을 입력하면 퀴즈로 넘어갑니다."

### Phase B (Turn 2)
1. references/main.md의 QUIZ 섹션 퀴즈 출제
2. 학생 답변에 피드백한다 (오답 해설 포함)
3. 다음 안내:
   - "웹에서 '완료' 버튼을 눌러주세요."
   - "C4 LAUNCH 챕터가 기다리고 있습니다! 다음: `/v4-warmup`"
   - "C4 미리보기: localhost에서만 보이던 서비스를 인터넷에 공개합니다!"

### 에러 대응 원칙
- GitHub 연결 오류 (SSH/HTTPS) 시 단계별 안내
- push 실패 시 오류 메시지를 Claude에게 전달

### 산출물
- 전체 기능 점검 완료
- GitHub 저장소에 코드 업로드
- C3 완료 인증
