---
name: v6-chatbot
description: "Claude API + 카카오톡 채널/디스코드 봇으로 본인 도메인 챗봇을 만듭니다. Triggers: \"v6 chatbot\", \"v6-chatbot\", \"챗봇 만들기\", \"카카오톡 챗봇\", \"디스코드 봇\", \"claude api 챗봇\""
---

# V6: 챗봇 만들기 실습

## 학습 목표
- Claude API가 정확히 뭐고 Claude Desktop과 어떻게 다른지 이해한다
- 본인 도메인에 맞는 채널(카카오톡 채널 / 디스코드 봇) 1개를 결정한다
- 본인 도메인 정보를 system prompt로 주입한 챗봇 1개를 실제로 띄우고, 친구/지인이 메시지를 보내면 답이 가는지 확인한다

## 사전 조건
- Ch.5 완료 또는 본인 SaaS 운영 중
- 본인 도메인의 FAQ가 있거나 정리할 수 있는 상태 (예: 카페 메뉴/시간, 본인 SaaS 가이드, 게임 공략)
- 결제 가능한 카드 (Claude API 사용 등록용 — 무료 크레딧 $5 부여)

## 대화형 학습 프로토콜

이 스킬은 대화형 코칭 방식으로 진행해요. 본인 도메인을 같이 정의하고, 채널을 결정하고, 코드/설정을 자동 생성해서 본인 PC에서 첫 메시지가 도착하는 것까지 함께해요.

### 진행 방식
1. references/main.md를 읽고 8개 Turn의 대화 흐름을 따라간다
2. 학습자의 도메인 → 채널 결정 → API 키 준비 → 채널 셋업 → 응답 코드 → 도메인 지식 주입 → 첫 메시지 테스트
3. 외부 도구(Anthropic Console / Discord Developer Portal / Kakao Business)는 학습자가 직접 클릭해야 하므로 화면 안내를 정확하게 한다
4. 산출물 파일을 작성해서 키 보관 위치, webhook URL, 다음 단계까지 정리한다

### 산출물
- 파일명: `learn-outputs/ch6-3-chatbot.md`
- 내용: 도메인 정보, 선택한 채널, API 키 보관 위치 안내, webhook URL, system prompt 전체 텍스트, Spend limit 설정 결과, 5개 테스트 질문/답변 기록
