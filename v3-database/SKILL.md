---
name: v3-database
description: "데이터베이스 + 모델 만들기. C3 BUILD 여섯 번째 스킬. Triggers: \"v3 database\", \"v3-database\", \"데이터베이스\", \"모델 만들기\""
---

# V3: 데이터베이스 + 모델 만들기

## 학습 목표
- 데이터베이스를 "엑셀 시트"로 이해한다
- 내 서비스에 필요한 데이터 구조를 설계한다
- Rails 모델을 생성하고 콘솔에서 데이터를 다뤄본다

## 사전 조건
- `/v3-git-save` 완료 (Git 기본 사용 경험)
- C2에서 작성한 설계서 (my-service-design-v1.0.md의 데이터 구조 참고)
- 코드 에디터 + Claude Code 확장 프로그램에서 진행

## STOP PROTOCOL

### Phase A (Turn 1)
1. references/main.md의 EXPLAIN 섹션을 읽고 설명한다
   - 데이터베이스 = 엑셀 (sheet=테이블, column=칼럼, row=데이터)
   - 칼럼 타입: string(짧은 글), text(긴 글), integer(숫자), boolean(예/아니오)
   - 마이그레이션 = 설계도 → 실제 건물
2. references/main.md의 EXECUTE 섹션을 따라 실행한다
   - C2 기획서 기반 데이터 구조 설계
   - 첫 번째 모델 생성 + 마이그레이션
   - Rails 콘솔에서 데이터 생성/조회
   - (선택) 두 번째 모델 + 관계 설정
3. **STOP** — 여기서 멈추고 학생의 응답을 기다린다.
4. 멈추기 전 출력: "데이터베이스와 모델을 만들었습니다. '다음'을 입력하면 퀴즈로 넘어갑니다."

### Phase B (Turn 2)
1. references/main.md의 QUIZ 섹션 퀴즈 출제
2. 학생 답변에 피드백한다 (오답 해설 포함)
3. 다음 안내:
   - "웹에서 '완료' 버튼을 눌러주세요."
   - "다음 스킬: `/v3-auth`"

### 에러 대응 원칙
- 마이그레이션 오류 시 Claude에게 오류 메시지 전달
- "User 모델은 여기서 만들지 않습니다" (v3-auth에서 처리)

### 산출물
- 최소 1개의 모델과 마이그레이션
- Rails 콘솔에서 데이터 CRUD 경험
- git commit
