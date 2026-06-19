## CONTEXT

이 스킬은 Ch.7에서 사용된다. 배포 완료 + 첫 사용자 경험 이후.
목적: n8n / Zapier / 자체 webhook 3가지 옵션을 비교하고, 본인 SaaS에 가입→Slack 알림+Notion 행 추가+환영 메일 흐름 중 1가지 이상을 실제로 연결한다.
Rails Solid Queue가 아니라 **외부 도구 연결**이 핵심.

---

## EXECUTE

### 인트로

다음 문장으로 시작한다:

> "안녕하세요! /v7-automation 시작합니다.
> 서비스가 배포됐으니 이제 '사람이 안 해도 되는 일'을 연결할 차례예요.
> 오늘은 가입 이벤트 하나를 자동화로 연결해볼게요. 30분이면 됩니다."

---

### 단계 1: 자동화 도구 선택 (10분)

먼저 3가지 옵션을 비교해서 설명한다:

| | n8n | Zapier | 자체 webhook (Rails) |
|--|-----|--------|-------------------|
| **난이도** | 중간 (셀프 호스팅 필요) | 쉬움 (웹 UI) | 어려움 (코드 작성) |
| **무료 범위** | 셀프 호스팅이면 무제한 | 100 task/월 무료 | 무제한 (서버 비용만) |
| **추천 대상** | 코드에 익숙해지면 | **첫 시도 강력 추천** | 이미 Rails 익숙 |
| **연결 가능** | 수백 개 서비스 | 수천 개 서비스 | 직접 구현한 것만 |
| **설정 시간** | 30~60분 | **5~15분** | 수 시간 |

> "첫 번째 자동화는 **Zapier**를 강력 추천해요. 로그인 후 클릭 몇 번이면 연결됩니다."

> "어떤 도구로 해볼까요? 이유도 한 줄로 말해 주세요."

학생 답 듣고 → 해당 도구 기준으로 다음 단계 진행.

---

### 단계 2: 트리거·액션 정하기 (10분)

> "자동화는 두 파트예요: 트리거(무엇이 일어나면) + 액션(무엇을 실행할지)."

**가장 많이 쓰는 가입 이벤트 자동화 흐름:**

```
트리거: 본인 SaaS에 새 사용자가 가입하면
   ↓
액션 A: Slack 채널에 알림 메시지 ("신규 가입: OOO님")
액션 B: Notion 데이터베이스에 행 추가 (이름, 이메일, 가입일)
액션 C: 환영 메일 발송 (SendGrid / Gmail)
```

> "이 중 오늘 연결해볼 액션을 골라봐요. 1개부터 시작해도 충분해요."

```
□ Slack 알림
□ Notion 행 추가
□ 환영 메일
```

학생이 선택하면 → 해당 액션 기준으로 안내.

---

### 단계 3: Zapier 연결 (20분)

**Zapier 기준 단계별 안내:**

**① Zapier 계정 준비**

> "zapier.com에 접속해서 무료 계정을 만들어요. Google 계정으로 1분이면 됩니다."

**② 새 Zap 만들기**

1. "Create Zap" 클릭
2. Trigger 검색: "Webhooks by Zapier" 선택
3. Event: "Catch Hook" 선택
4. "Continue" → Webhook URL 복사

> "이 URL이 트리거 주소예요. 본인 Rails 서비스가 이 URL로 데이터를 보내면 자동으로 실행돼요."

**③ Rails에 webhook 전송 코드 추가**

Claude Code에서:

```
사용자가 가입할 때 Zapier webhook으로 데이터를 보내는 코드를 추가해줘.

webhook URL: [Zapier에서 받은 URL]
보낼 데이터:
- user_email
- user_name
- signed_up_at (현재 시각)

User 모델의 after_create 콜백 또는 RegistrationsController에 추가해줘.
비동기로 보내서 가입 속도에 영향 없게 해줘.
```

**④ 테스트 전송**

> "Zapier가 'Waiting for data...' 상태가 됐으면, 본인 서비스에서 테스트 계정으로 가입해보세요."

가입 후 Zapier로 돌아와서 "Test trigger" → 데이터가 들어왔는지 확인.

**⑤ 액션 연결**

*Slack 알림 선택한 경우:*
1. "+" 클릭 → Action 추가
2. Slack 검색 → "Send Channel Message" 선택
3. Slack 계정 연결 → 채널 선택
4. 메시지 작성: `신규 가입 🎉 {{user_name}} ({{user_email}}) — {{signed_up_at}}`

*Notion 행 추가 선택한 경우:*
1. Notion 검색 → "Create Database Item" 선택
2. Notion 계정 연결 → 대상 DB 선택
3. 필드 매핑: 이름 → `{{user_name}}`, 이메일 → `{{user_email}}`

*환영 메일 선택한 경우:*
1. Gmail 또는 SendGrid 선택
2. Gmail: "Send Email" → 수신자 `{{user_email}}` → 제목·본문 작성

**⑥ 최종 테스트**

> "Zap을 "Publish"하고, 서비스에서 다시 한 번 가입 테스트를 해보세요."

Slack/Notion/메일에 자동으로 무언가 도착하면 성공!

---

### 단계 4: n8n 선택한 경우 안내

> "n8n은 셀프 호스팅이 필요해요. 가장 빠른 방법은 Railway에 n8n을 1분 배포하는 것이에요."

```
1. railway.app → "New Project" → "Template" 검색 → "n8n" 선택
2. Railway가 n8n을 자동 배포 (1~2분)
3. 생성된 URL로 접속 → n8n 웹 UI 열림
4. 이후 Zapier와 동일한 흐름 (Webhook → Action)
```

> "n8n은 복잡한 자동화나 여러 단계가 필요할 때 강력해요. 지금 당장은 Zapier가 빠릅니다."

---

### 단계 5: 자체 webhook 선택한 경우 안내

> "Rails로 직접 구현하면 가장 자유롭지만 코드가 필요해요."

Claude Code에서:

```
가입 이벤트 발생 시 다음 처리를 하는 코드를 추가해줘:

1. Slack webhook으로 메시지 전송
   - SLACK_WEBHOOK_URL 환경변수 사용
   - 메시지: "신규 가입: [이름] ([이메일])"

2. 비동기 처리 (ActiveJob 사용)
   - 가입 속도에 영향 없게

.env에 SLACK_WEBHOOK_URL 추가하는 방법도 알려줘.
```

> "Slack incoming webhook URL은 Slack API 사이트(api.slack.com)에서 발급해요. 'Create App' → 'Incoming Webhooks' 활성화 → URL 복사."

---

### 마무리: 파일 저장 + 다음 단계

학생의 진행 내용을 `my-automation.md` 파일로 **실제 생성**한다:

```markdown
# 자동화 실습 결과

## 선택한 도구
- 도구: [Zapier / n8n / 자체 webhook]
- 선택 이유: [학생이 말한 이유]

## 연결한 흐름
트리거: 본인 SaaS에 새 사용자 가입
   ↓
액션 1: [Slack 알림 / Notion 행 추가 / 환영 메일 — 선택한 것]

## 테스트 결과
- 테스트 가입 계정: (마스킹)
- 결과: [성공 / 실패 + 오류 메시지]

## 비용 메모
- [선택한 도구] 요금제: [무료 / 유료]
- 월 예상 task 수: [추정값]
- 무료 한도 내 가능 여부: [가능 / 불가능]

## 다음 자동화 후보
- [ ] [다음에 추가하고 싶은 자동화]
```

저장 후:

> "축하해요! 이제 서비스가 자는 동안에도 Slack·Notion·메일이 움직입니다.
> 다음은 Ch.8 — 수익화 (결제·구독) 또는 본인 페이스에 맞게 다음 챕터로 이동하세요."

---

## 자주 막히는 지점

**"Zapier에서 데이터가 안 들어와요"**
→ Zap이 "Waiting for data" 상태인지 확인. 가입 테스트는 Zap이 켜진 후에 해야 잡힙니다. 서버 로그에서 `HTTP POST [webhook URL]` 요청이 나가는지 확인.

**"Rails에서 webhook 전송 시 가입이 느려져요"**
→ 동기 방식으로 보내고 있는 것. ActiveJob으로 비동기 처리하도록 수정 필요. Claude Code에 "webhook 전송을 비동기로 바꿔줘"라고 하면 됩니다.

**"Notion 연결이 안 돼요"**
→ Notion Integration이 해당 DB에 공유됐는지 확인. Notion → DB 설정 → "공유" → Integration 추가.

**"무료 플랜에서 task가 금방 다 써요"**
→ 월 100 task는 하루 3건 정도. 서비스가 성장하면 n8n 셀프 호스팅으로 전환하거나 Zapier Starter 플랜($20/월)으로 업그레이드.
