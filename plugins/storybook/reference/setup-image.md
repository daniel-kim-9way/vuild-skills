# 그림 엔진 준비

## Codex (ChatGPT 구독)

필요한 것: ChatGPT 유료 플랜(Plus 이상), Node.js 18 이상. 추가 비용은 없어요. 한 장에 1~3분 걸려요.

1. 설치: `npm install -g @openai/codex` (Node.js가 없으면 nodejs.org에서 LTS를 먼저 깔아요)
2. 로그인: 터미널에서 `codex login` → 브라우저가 열리면 **ChatGPT 계정으로** 로그인해요. API 키로 로그인하지 않아요. 동화 공방은 API 키 경로를 쓰지 않아요.
3. 확인: `sb codex check` → «✓ ChatGPT 계정으로 로그인돼 있어요»
4. 시험: `sb draw-test` (1~3분, 주황 곰 그림이 열려요)

- WSL: 리눅스 쪽에 Codex가 없으면 윈도우에 깔린 Codex를 찾아 써요. 윈도우 PowerShell에서 1~2번을 해도 돼요.
- ChatGPT 사용량 한도에 걸리면 멈추고 알려 줘요. 한도가 풀린 뒤 «이어서 그려 줘»라고 하면 안 그린 쪽만 그려요.

## fal.ai

필요한 것: 카드. 한 장에 80~130원, 동화 한 편(9장)에 700~1,100원쯤 들어요. 9장에 3분쯤 걸려요.

1. fal.ai에 가입해요.
2. Billing에서 충전해요(처음에는 5~10달러면 넉넉해요).
3. API Keys에서 새 키를 만들고 복사해요.
4. `sb env open` → `FAL_KEY=` 뒤에 붙여 넣고 저장해요.
5. 확인: `sb doctor` → «그림: fal.ai (FAL_KEY 있음)»
6. 시험: `sb draw-test` (100원 안팎)

- 그린 결과를 fal 기록에 남기지 않게 요청해요(아이 사진이 들어가서요).
