---
name: v7-automation
description: "자동화 실습 스킬. n8n / Zapier / 자체 webhook 3가지 옵션을 비교하고, 본인 SaaS에 가입→Slack 알림+Notion 행 추가+환영 메일 흐름을 실제로 연결한다. Triggers: \"v7-automation\", \"자동화\", \"Slack 연결\", \"Notion 연결\", \"webhook\", \"Zapier\", \"n8n\""
---

# V7: 자동화 실습 — Slack/Notion/메일 연결

## 목표
- n8n / Zapier / 자체 webhook 3가지 옵션의 차이와 본인 상황에 맞는 선택을 안다
- 본인 SaaS에 자동화 흐름 1개를 실제로 연결한다 (예: 가입 → Slack 알림 + Notion 행 추가 + 환영 메일)
- 트리거·액션·webhook 개념을 실제 연결로 익힌다

## 사전 조건
- 배포 완료 (인터넷 URL 있음, Ch.5)
- Claude Code 터미널에서 실행

## 진행 방식

1. `references/main.md`를 읽고 도구 선택부터 시작한다
2. Q&A로 트리거(무엇이 일어나면)와 액션(무엇을 실행할지)을 정한다
3. 선택한 도구(Zapier 권장 첫 시도)로 단계별 연결을 안내한다
4. 실제 가입 테스트로 자동화가 동작하는지 확인한다

## 산출물
- 파일명: `my-automation.md`
- 내용: 선택한 도구 + 연결한 흐름(트리거 → 액션 목록) + 테스트 결과 + 비용 메모
