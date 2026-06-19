---
name: v4-payment
description: "[선택] 결제 연동 (Toss Payments). Triggers: \"v4 payment\", \"v4-payment\", \"결제\", \"토스페이먼츠\""
---

# [선택] 결제 연동 (Toss Payments)

## 학습 목표
- 결제 흐름 전체를 이해한다 (고객 → 게이트웨이 → 내 통장)
- 테스트 모드로 결제 기능을 안전하게 구현할 수 있다
- 실제 서비스 운영을 위한 사업자등록 필요성을 안다

## 사전 조건
- `/v4-landing` 완료 (랜딩 페이지 완성)
- 코드 에디터 + Claude Code 확장 프로그램에서 진행

## 대화형 학습 프로토콜

### 진행 방식
1. references/main.md의 EXPLAIN 섹션을 읽고 설명한다
   - "테스트 모드에서는 실제 돈이 안 오갑니다" (안심시키기)
   - 결제 흐름 전체 설명
   - Toss Payments 선택 이유
2. references/main.md의 EXECUTE 섹션을 따라 실행한다
   - Toss 테스트 모드 설정
   - 가격 페이지 구현
   - 결제 흐름 구현
   - 테스트 결제 실행
3. **STOP** — 학생 응답 대기
4. references/main.md의 QUIZ 섹션 퀴즈 출제
5. 다음 안내: `/v4-security`

### 산출물
- Toss Payments 테스트 결제 성공
- 결제 흐름 전체 동작 확인
