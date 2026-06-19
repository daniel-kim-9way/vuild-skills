---
name: v3-env
description: "API 키·비밀값을 .env(또는 Rails credentials)에 안전하게 두고, ANTHROPIC_API_KEY / OPENAI_API_KEY를 발급해서 본인 서비스에 AI 기능 3가지(자동 요약 / 자동 분류 / 자동 답변 초안)를 붙이는 기초. Triggers: \"v3 env\", \"v3-env\", \"환경변수\", \"API 키\", \".env\", \"ANTHROPIC_API_KEY\", \"OPENAI_API_KEY\""
---

# V3: 환경변수 + LLM 키 + AI 기능 사례

## 학습 목표
- API 키·비밀번호를 코드에 직접 적으면 왜 위험한지 이해한다
- `.env` 파일과 Rails credentials의 차이를 알고, 본 코스 권장(`.env`)으로 본인 키를 보관한다
- Anthropic Console에서 `ANTHROPIC_API_KEY`를 발급해서 `.env`에 등록한다 (선택: OpenAI도)
- 본인 SaaS에 AI 기능을 붙일 수 있는 3가지 패턴(자동 요약 / 자동 분류 / 자동 답변 초안)을 알고, 그중 1개를 본인 서비스에 적용할 후보로 정한다

## 사전 조건
- Ch.4-3 완료 (git이 본인 PC에 깔려 있고 `.gitignore` 개념 한 번 들어 본 적 있음)
- Ch.4-5 완료 (`.env` 파일이 본인 빌드킷 폴더에 이미 존재 — `cp .env.example .env`로 복사된 상태)
- Anthropic 계정 + 결제 카드 1장 (사용 한도 설정 시 무료 크레딧으로도 시작 가능)

## 대화형 학습 프로토콜

이 스킬은 대화형 코칭 방식을 따릅니다. 강의가 아닌 질문-답변-피드백 루프로 진행합니다.

### 진행 방식
1. references/main.md를 읽고 대화 흐름(Turn 1 ~ Turn 8)에 따라 진행
2. 학생이 본인 PC에서 `.env` 파일을 직접 열어 보고, Anthropic Console에서 키를 발급해서 본인 손으로 `.env`에 추가
3. 마지막에 본인 서비스에 어떤 AI 기능이 어울릴지 한 줄로 정의 → 신규 티켓 1개의 후보로 저장
4. 산출물을 파일로 저장

### 산출물
- 파일명: `learn-outputs/ch4-13-env.md`
- 내용: `.env` 안에 등록한 키 목록 (값은 마스킹) + 본인 서비스의 AI 기능 후보 1개의 한 줄 정의 + 신규 티켓 초안
