---
name: v1-discover
description: "Claude AI 도구 발견 + 비용 시뮬레이터. claude.ai / Claude Desktop / Claude Code / API 4가지 차이를 정리하고, 예산·학습 속도 기반 구독 플랜을 추천하고, API 비용 알람을 설정하도록 안내한다. Triggers: \"v1-discover\", \"AI 도구 추천\", \"Claude 플랜\", \"비용 시뮬레이터\""
---

# V1: AI 도구 발견 + 비용 시뮬레이터

## 목표
- Claude 4가지 도구(claude.ai / Desktop / Code / API)의 역할 차이를 본인 말로 정리한다
- 예산·학습 속도·AI 기능 계획을 바탕으로 최적 구독 플랜을 고른다
- Anthropic Console에서 API 비용 한도 + 알람을 설정해 둔다

## 사전 조건
- Claude Desktop 설치 완료 (Ch.0-2)
- 이 스킬은 Claude Desktop 슬래시 스킬로 실행

## 진행 방식

1. `references/main.md`를 읽고 대화 흐름을 따른다
2. 질문 5개를 순서대로 한 번에 하나씩 묻는다 (한꺼번에 쏟지 않는다)
3. 답변을 바탕으로 플랜을 추천하고 이유를 설명한다
4. API 비용 알람 설정 방법을 안내한다
5. 결과를 `my-claude-plan.md`로 저장한다

## 산출물
- 파일명: `my-claude-plan.md`
- 내용: 추천 플랜 + 근거 + API 알람 설정 체크리스트
