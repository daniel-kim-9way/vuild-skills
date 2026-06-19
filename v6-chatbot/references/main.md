## EXPLAIN

### Claude API가 정확히 뭐예요?

지금까지 본인이 쓴 Claude는 **Claude Desktop** (앱)이나 **Claude Code** (터미널)였어요. 둘 다 사람이 손으로 입력하면 화면에 응답이 떠는 형태예요.

이번 lesson의 주인공인 **Claude API**는 다르게 동작해요. 본인 코드(예: Rails 컨트롤러) 안에서 "Claude야, 이 메시지에 답해 줘"라고 호출하면, 코드가 응답 문자열을 받아서 다른 곳(카톡/디스코드/본인 SaaS 화면)으로 다시 보낼 수 있어요.

쉽게 말해 **Claude를 사람 손이 아니라 코드가 호출**해서, 결과를 다른 채널로 흘려 보내는 방식이에요. 이 패턴 한 번 익히면 카톡 봇·디스코드 봇·본인 SaaS 안의 AI 도우미·자동 답변 메일까지 전부 같은 패턴으로 만들 수 있어요.

### 비유 — 식당 종업원과 주방장

ChatGPT/Claude Desktop은 **카운터에 직접 가서 주문하는 손님**이에요. 본인이 가서 말해야 답이 와요.

Claude API는 **종업원이 대신 주방에 주문을 전달하는 방식**이에요. 손님(카톡 사용자)이 종업원(본인 webhook)에게 말하면, 종업원이 주방(Claude API)에 주문을 넘기고, 음식(응답)을 받아와서 손님에게 전달해요. 손님은 주방을 직접 만나지 않아요.

### 왜 본인 도메인 챗봇인가?

일반 ChatGPT는 "세상 모든 질문"에 답해요. 그래서 본인 카페 메뉴는 모르고, 본인 SaaS 사용법도 모르고, 본인 게임 공략도 몰라요.

본인 도메인 챗봇은 정반대예요. **딱 본인 도메인 안의 질문만** 정확히 답해요. 도메인이 좁을수록 정확도가 높아요. 너무 넓으면(예: "세상 모든 질문") 일반 ChatGPT 쓰는 게 나아요.

### 2가지 채널 — 카카오톡 vs 디스코드

| 채널 | 강점 | 약점 | 추천 도메인 |
|---|---|---|---|
| 카카오톡 채널 | 한국 사용자 100% 도달 | 사업자 등록 + 채널 승인(보통 1~2일) 필요 | 카페·숍·예약·B2C 고객 응대 |
| 디스코드 봇 | 30분 안에 동작, 승인 절차 0 | 디스코드 사용자만 접근 | 개발자 커뮤니티·팬덤·게임·스터디 |

**처음이라면 디스코드부터.** 승인 절차 없이 30분 안에 동작하는 봇을 띄울 수 있어요. 친구 5명을 디스코드 서버에 초대해서 테스트해 보세요. 그 흐름이 완성되면 같은 응답 코드를 카카오톡 webhook 형식으로 옮기면 돼요.

---

## EXECUTE

### Turn 1: 도메인 결정

> "안녕하세요. 본인 도메인 챗봇을 만드는 시간이에요. 챗봇을 띄우려면 먼저 '무엇에 대해 답하는' 챗봇인지를 정해야 해요."

> "질문 1개 — **어떤 도메인의 챗봇을 만들고 싶어요?** 예시:"

```
- 본인 SaaS의 사용법/FAQ ("우리 서비스 결제는 어떻게 해요?")
- 본인 카페·숍의 영업 정보 ("오늘 영업해요?", "케이크 남았어요?")
- 본인 게임/콘텐츠 공략 ("X 보스 어떻게 잡아요?")
- 본인 분야 Q&A 봇 ("초보 베이커가 식빵 팽창 안 될 때?")
- 독서 추천 봇 ("내 취향에 맞는 다음 책?")
```

> "위 예시 중 하나를 골라도 되고, 본인만의 도메인을 적어도 돼요. 한 줄로 적어 주세요."

학습자 답변을 받으면:
> "좋아요. **[도메인]** 챗봇으로 가요."

> "다음 — 그 도메인에서 사용자가 자주 묻는 질문 **5개**를 알려 주세요. 짧게 적어도 돼요. 이 5개가 챗봇 정확도를 결정해요."

학습자가 5개를 적으면 다음 Turn으로. 5개를 못 적으면:
> "괜찮아요. 떠오르는 거 3개라도 좋아요. 나머지는 챗봇 운영하면서 채워 나가요."

---

### Turn 2: 채널 결정 (카톡 vs 디스코드)

> "도메인이 정해졌으니 이제 **사용자가 어디 모여 있는지**를 봐요. 그 곳에 챗봇을 띄워야 사람이 와요."

> "두 가지 옵션 비교:"

```
1. 카카오톡 채널
   ✓ 한국 사용자 거의 100% 도달
   ✗ 카카오비즈니스 가입 + 채널 승인 1~2일
   → 일반 고객 대상 (카페·숍·예약·B2C)

2. 디스코드 봇
   ✓ 30분 안에 봇 띄우기 가능, 승인 0
   ✗ 디스코드 사용자만 접근 가능
   → 커뮤니티·팬덤·게임·스터디·개발자
```

> "본인 도메인이라면 어느 채널이 더 맞을까요?"

학습자 응답 기반 추천:
- 도메인이 "카페·숍·예약·일반 고객" → **카카오톡 채널**
- 도메인이 "커뮤니티·팬덤·게임·개발자" → **디스코드 봇**
- 처음이거나 망설인다면 → **디스코드 봇** (빠르고 승인 없어서 학습 효과 큼. 흐름 완성 후 카톡으로 옮기면 됨)

> "**[채널]** 으로 가요. 다음 Turn에서 Claude API 키부터 준비해요."

---

### Turn 3: Claude API 키 발급

> "Claude API 키는 본인 비밀번호 같은 거예요. 이 키로 Claude를 호출하면 본인 계정에 비용이 청구돼요. 그래서 다음 두 가지를 꼭 지켜요: (1) 절대 GitHub 같은 공개 저장소에 올리지 않기, (2) 발급 후 즉시 비밀번호 매니저나 안전한 곳에 저장."

> "발급 단계 — **본인이 브라우저에서 직접 클릭**해야 해요:"

```
1. https://console.anthropic.com 접속
2. 로그인 (없으면 가입 — 무료 크레딧 $5 자동 부여)
3. 좌측 메뉴 → "API Keys" 클릭
4. 우상단 "Create Key" 버튼 클릭
5. 이름 입력 (예: "my-chatbot"), 권한은 기본값 그대로
6. "Create Key" → 발급된 키 복사 (sk-ant-... 로 시작)
```

> "⚠️ **중요**: 이 키는 발급 직후 **단 1회만** 보여요. 페이지를 닫으면 다시 못 봐요. 즉시 (1) 비밀번호 매니저(1Password/Bitwarden) 또는 (2) 본인 PC의 메모장에 임시 저장."

> "발급 완료했나요? 다음으로 가기 전에 **Spend limit (월 사용 한도)** 도 같이 설정해요. 봇이 무한 루프 돌거나 악성 사용자가 폭주해도 본인이 청구서 폭탄 안 맞게."

```
1. 같은 console.anthropic.com에서 좌측 "Settings" → "Billing" → "Limits"
2. "Monthly spend limit" 입력 (처음이라면 $10 추천 — 약 1만 3천 원)
3. 저장
```

> "이렇게 하면 한 달에 $10 이상 청구 절대 안 가요. 익숙해지면 한도를 늘리세요."

> "키 발급 + Spend limit 설정 완료했으면 다음 Turn으로."

---

### Turn 4: 선택한 채널 셋업

학습자가 디스코드를 골랐는지 카톡을 골랐는지에 따라 분기.

#### 디스코드 봇 셋업 (선택 시)

> "디스코드 봇은 6단계예요. 본인이 클릭해야 하니 천천히 따라오세요."

```
1. https://discord.com/developers/applications 접속 → 로그인
2. 우상단 "New Application" 클릭 → 이름 입력 (예: "MyDomainBot") → Create
3. 좌측 "Bot" 메뉴 클릭 → "Reset Token" 또는 "Copy" 버튼으로 봇 토큰 복사
   ⚠️ 이 토큰도 1회만 보여요. 즉시 안전한 곳에 저장.
4. 같은 페이지에서 "MESSAGE CONTENT INTENT" 토글을 ON
   (이거 꺼 있으면 봇이 메시지 내용을 못 읽어요)
5. 좌측 "OAuth2" → "URL Generator"
   - Scopes: "bot" 체크
   - Bot Permissions: "Read Messages/View Channels", "Send Messages", "Read Message History" 체크
6. 하단에 생성된 URL 복사 → 새 탭에서 열기 → 본인 디스코드 서버 선택 → "Authorize"
```

> "이제 본인 디스코드 서버에 봇이 멤버로 추가됐어요. 서버에 봇 이름이 보이면 성공이에요."

> "테스트용 디스코드 서버가 없다면? 디스코드 앱 좌측 하단 "+" → "내가 직접 만들기" → 이름 입력. 5초면 만들어져요."

> "준비된 정보:"
> "- Discord Bot Token: `<학습자가 복사한 토큰>`"
> "- Anthropic API Key: `<Turn 3에서 받은 키>`"
> "- 본인 도메인 정보 5개"

> "다음 Turn에서 이 3가지로 응답 코드를 만들어요."

#### 카카오톡 채널 셋업 (선택 시)

> "카카오톡 채널은 디스코드보다 단계가 많아요. 그리고 사업자 정보가 필요해요."

```
1. https://business.kakao.com 접속 → 카카오 계정으로 로그인
2. "카카오톡 채널" 메뉴 → "채널 만들기"
3. 사업자 정보 입력 (개인사업자도 가능. 사업자등록증 사진 업로드)
4. 채널 이름·검색용 아이디 입력 → 신청
5. 보통 1~2일 후 승인 메일
```

> "**승인 대기 중에는 디스코드로 먼저 흐름을 익히는 것을 강력 추천**해요. 같은 응답 코드를 나중에 카톡 webhook 형식으로 5분이면 옮겨요. 디스코드부터 갈까요? (Y/N)"

학습자가 "Y" → 디스코드 셋업 안내로 분기.
학습자가 "N, 카톡으로 끝까지" → 다음 단계 안내:

```
6. 승인 후: 카카오 i 오픈빌더 (https://i.kakao.com) 가입
7. "봇 만들기" → 본인 채널 연결
8. 좌측 "스킬" 메뉴 → "스킬 만들기"
9. 본인 webhook URL 입력 (다음 Turn에서 본인 SaaS에 만들 예정)
10. 시나리오 → "폴백 블록"에 방금 만든 스킬 연결 (모든 메시지를 webhook으로 보내는 기본 흐름)
```

> "준비된 정보:"
> "- 카카오 채널 ID: `<학습자 채널 ID>`"
> "- 카카오 i 오픈빌더 봇 ID: `<봇 ID>`"
> "- Anthropic API Key: `<Turn 3에서 받은 키>`"

> "다음 Turn에서 webhook 응답 코드를 만들어요."

---

### Turn 5: 챗봇 응답 로직 코드 생성

학습자의 채널 + 도메인 정보 기반으로 실제 코드를 생성.

#### 디스코드 봇 코드 (Node.js, 가장 빠름)

생성 위치: `chatbot-discord/` 폴더

`package.json`:
```json
{
  "name": "<도메인>-chatbot",
  "version": "0.1.0",
  "type": "module",
  "scripts": { "start": "node bot.js" },
  "dependencies": {
    "discord.js": "^14.14.1",
    "@anthropic-ai/sdk": "^0.27.0",
    "dotenv": "^16.4.5"
  }
}
```

`.env` (학습자가 직접 채움):
```
DISCORD_BOT_TOKEN=<디스코드 봇 토큰>
ANTHROPIC_API_KEY=<Anthropic 키>
```

`.gitignore`:
```
.env
node_modules/
```

`bot.js`:
```javascript
import "dotenv/config";
import { Client, GatewayIntentBits } from "discord.js";
import Anthropic from "@anthropic-ai/sdk";

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});
const anthropic = new Anthropic();

const SYSTEM_PROMPT = `<Turn 6에서 학습자 도메인 정보로 채워짐>`;

client.on("messageCreate", async (msg) => {
  if (msg.author.bot) return;
  // /ask 명령으로만 응답 (전체 메시지 응답하지 않음)
  if (!msg.content.startsWith("/ask")) return;
  const question = msg.content.replace(/^\/ask\s*/, "").trim();
  if (!question) {
    msg.reply("질문을 적어 주세요. 예: `/ask 영업시간 알려줘`");
    return;
  }

  await msg.channel.sendTyping();
  try {
    const res = await anthropic.messages.create({
      model: "claude-sonnet-4-5",
      max_tokens: 500,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: question }],
    });
    const text = res.content[0].text;
    msg.reply(text);
  } catch (e) {
    console.error(e);
    msg.reply("죄송해요, 잠시 후 다시 시도해 주세요.");
  }
});

client.login(process.env.DISCORD_BOT_TOKEN);
```

> "터미널에서 실행:"
```
cd chatbot-discord
npm install
npm start
```

> "성공하면 `Logged in as <봇 이름>` 같은 메시지가 떠요. 봇이 디스코드 서버에서 '온라인'으로 보이면 OK."

#### 카카오톡 webhook 코드 (Rails 기준)

생성 위치: 본인 Rails 앱 안에 추가.

`app/controllers/chatbot_controller.rb`:
```ruby
class ChatbotController < ApplicationController
  skip_forgery_protection

  def kakao_incoming
    user_message = params.dig("userRequest", "utterance").to_s.strip
    answer = ChatbotResponder.new.respond(user_message)
    render json: {
      version: "2.0",
      template: { outputs: [{ simpleText: { text: answer } }] },
    }
  end
end
```

`app/services/chatbot_responder.rb`:
```ruby
class ChatbotResponder
  SYSTEM_PROMPT = <<~PROMPT
    <Turn 6에서 학습자 도메인 정보로 채워짐>
  PROMPT

  def respond(user_message)
    return "질문을 적어 주세요." if user_message.empty?

    res = HTTP.headers(
      "x-api-key" => ENV.fetch("ANTHROPIC_API_KEY"),
      "anthropic-version" => "2023-06-01",
      "content-type" => "application/json"
    ).post("https://api.anthropic.com/v1/messages", json: {
      model: "claude-sonnet-4-5",
      max_tokens: 500,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: user_message }],
    })
    res.parse.dig("content", 0, "text") || "잠시 후 다시 시도해 주세요."
  rescue => e
    Rails.logger.error("[chatbot] #{e.message}")
    "잠시 후 다시 시도해 주세요."
  end
end
```

`config/routes.rb` 추가:
```ruby
post "chatbot/kakao", to: "chatbot#kakao_incoming"
```

`.env` 추가:
```
ANTHROPIC_API_KEY=<Anthropic 키>
```

> "주의: 카카오 i 오픈빌더의 스킬 등록 시 webhook URL은 **HTTPS + 공인 도메인** 이어야 해요. 로컬 개발 중이면 ngrok로 임시 URL을 받아서 등록하세요. 배포 후에는 본인 서비스 도메인으로 교체."

---

### Turn 6: 본인 도메인 지식 주입 (System Prompt)

> "이제 챗봇의 핵심 — **본인 도메인 정보를 system prompt에 주입**해요. 이게 정확도를 결정해요."

> "Turn 1에서 적은 도메인 + 5개 질문을 바탕으로 system prompt를 같이 만들어요. 다음 정보가 더 필요해요:"

도메인별 질문 템플릿:

**카페·숍 도메인이라면:**
- 영업 시간 (평일/주말 따로)
- 메뉴와 가격 (대표 메뉴 5~10개)
- 위치·주차·예약 가능 여부
- 응대 톤 (친근하게/공손하게/유머 있게)

**SaaS 사용법 도메인이라면:**
- 서비스 한 줄 정의
- 주요 기능 3~5개
- 가격 정책
- 자주 묻는 질문 답변
- 응대 톤

**커뮤니티·게임 도메인이라면:**
- 커뮤니티 한 줄 소개
- 자주 묻는 질문 + 답변
- 신규 멤버 안내 사항
- 응대 톤

> "본인 도메인에 해당하는 정보를 정리해서 보내 주세요. 표 형식이든 줄글이든 OK. 적은 만큼 정확도가 올라가요."

학습자 정보를 받으면 system prompt 자동 생성:

```
당신은 [도메인 한 줄 정의]의 친절한 챗봇입니다.

== 도메인 정보 ==
[학습자가 보낸 모든 정보를 그대로 또는 정리해서 삽입]

== 답변 규칙 ==
1. 위 도메인 정보 안에서만 답하세요.
2. 모르는 내용은 추측하지 말고 "잘 모르겠어요. [본인 연락처]로 문의 부탁드립니다"라고 답하세요.
3. 답변은 간결하게 (3문장 이내). 친근하지만 전문적으로.
4. 답변 마지막에 다음 액션을 1개 제안하세요 (예: "예약하시려면 이쪽으로...", "메뉴 더 보시려면...").
5. 본인이 [도메인 운영자]가 아니라는 사실을 사용자에게 굳이 말하지 마세요.
```

이 system prompt를 학습자의 코드(`bot.js`의 `SYSTEM_PROMPT` 또는 `chatbot_responder.rb`의 `SYSTEM_PROMPT` 상수)에 삽입.

> "이제 본인 도메인 챗봇이 준비됐어요. 다음 Turn에서 첫 메시지를 보내 봐요."

---

### Turn 7: 첫 메시지 테스트

#### 디스코드의 경우

> "디스코드 서버에서 본인 봇이 추가된 채널로 가요. 본인이 메시지를 보내요:"

```
/ask 영업시간 알려줘
```

(또는 본인 도메인에 맞는 질문)

> "5초 정도 후 봇이 응답을 보내요. **본인 도메인 정보 안에서 정확한 답이 오면 성공**이에요."

확인 사항:
- ✅ 봇이 응답함
- ✅ 답이 본인 도메인 정보와 일치함
- ✅ 모르는 질문에는 "전화로 문의 부탁드립니다" 같은 fallback 답변이 나옴

봇이 응답 안 하면:
> "체크 리스트:"
> "1. 터미널에서 `npm start` 가 살아 있나요? 죽어 있으면 다시 실행."
> "2. 디스코드 Developer Portal에서 'MESSAGE CONTENT INTENT'가 ON 인가요?"
> "3. 봇이 해당 채널에 'Send Messages' 권한이 있나요?"
> "4. 메시지가 정확히 `/ask`로 시작하나요? 공백 1개 차이도 영향."

답이 부정확하면:
> "system prompt에 본인 정보를 더 풍부하게 넣어요. 예: 메뉴 정보가 너무 간단하면 가격, 사이즈, 옵션까지 추가."

#### 카카오톡의 경우

> "카카오 i 오픈빌더에서 좌상단 '시뮬레이터' 또는 '봇 테스트' 버튼을 눌러요."

> "테스트 입력창에 본인 도메인 질문 1개를 보내요:"

```
영업시간 알려줘
```

> "정확한 답이 오면 성공. 안 오면:"
> "1. 본인 webhook URL이 살아 있나요? (서버 동작 중?)"
> "2. webhook URL이 HTTPS 인가요?"
> "3. 본인 서버 로그에 카카오 요청이 찍히나요? 안 찍히면 카카오 → 본인 서버 네트워크 문제."

> "테스트가 OK면 본인 채널을 친구 1명에게 추가해서 진짜 사용자처럼 메시지 보내 보세요."

5개 테스트 질문/답변을 학습자가 적게 하기:
> "본인이 5개 질문을 보내고, 각각 어떤 답이 왔는지 적어 주세요. 정확하지 않은 답이 있으면 system prompt를 수정해서 다시 시도해요."

---

### Turn 8: 산출물 저장 + 다음 lesson 안내

> "본인 도메인 챗봇 1개가 살아 움직여요. 사용자가 보낸 메시지에 본인 도메인 정보로 답해요. 이게 본인이 잠을 자도 굴러가는 첫 자동 응대 흐름이에요."

> "오늘 만든 내용을 정리한 파일을 만들어 드려요. 키 위치, webhook URL, system prompt 전문이 들어가요. 나중에 수정하거나 친구한테 공유할 때 이 파일을 보세요."

`learn-outputs/ch6-3-chatbot.md` 파일 생성:

```markdown
# Ch.6-3 — 내 도메인 챗봇

## 도메인
[학습자 도메인 한 줄]

## 사용자가 자주 묻는 질문 5개
1. ...
2. ...
3. ...
4. ...
5. ...

## 채널
[디스코드 / 카카오톡]

## 키 보관 위치 (절대 GitHub에 올리지 말 것)
- Anthropic API Key: [학습자가 저장한 위치 — 1Password/Bitwarden/.env 등]
- Discord Bot Token (또는 카카오 토큰): [위치]
- Spend limit: $10/월 (필요 시 조정)

## webhook / 봇 정보
- 디스코드 서버 ID: <ID>
- 디스코드 채널: <채널 이름>
- (또는) 카카오 webhook URL: https://...

## System Prompt 전문
```
[Turn 6에서 만든 system prompt 전체 텍스트]
```

## 코드 위치
- 디스코드: chatbot-discord/bot.js
- (또는) 카카오: app/controllers/chatbot_controller.rb + app/services/chatbot_responder.rb

## 5개 테스트 질문/답변 기록
| 질문 | 답변 | 정확? |
|---|---|---|
| ... | ... | ✅/❌ |

## 운영 체크리스트
- [ ] Spend limit 설정 완료
- [ ] .env 파일이 .gitignore에 들어 있음
- [ ] 5개 테스트 질문 모두 ✅
- [ ] 친구 1명에게 알려서 진짜 사용자 1명 확보
- [ ] 1주일 후 잘못 답한 사례 5개 모아서 system prompt 보강

## 다음 단계
- 도메인 정보가 자주 바뀌면 (예: 매일 메뉴 변경): system prompt를 동적으로 만들기 (DB에서 매일 fetch)
- 봇이 답 못한 질문을 별도 DB에 쌓기 → 운영자가 주기적으로 확인 → system prompt 보강 루프
- 다음 lesson(6-4 크롬 확장)에서는 본인 브라우저에서 같은 패턴 활용

## 다음 lesson
- 6-4 크롬 확장 만들기 — 챗봇이 "사용자가 우리에게 오는" 흐름이라면, 크롬 확장은 "우리가 사용자의 브라우저로 가는" 흐름
```

마무리:
> "본인 첫 챗봇이 살아 움직여요. 잠을 자도 본인 대신 답해요."

> "잠깐 정리:"
> "1. Claude API 키를 발급해서 본인 코드가 Claude를 호출하게 했어요."
> "2. 디스코드/카톡 채널을 셋업했어요."
> "3. 본인 도메인 정보를 system prompt로 주입했어요."
> "4. 첫 메시지가 정확한 답으로 돌아왔어요."

> "이게 모든 AI 자동 응대의 기본 패턴이에요. 채널만 바꾸면 같은 코드를 메일/Slack/본인 SaaS 채팅에도 그대로 써요."

> "다음 lesson은 6-4 크롬 확장이에요. `/v6-chrome-ext` 또는 학습 사이트의 다음 lesson을 열어 주세요."

---

## 막히는 지점 — 미리 답

**① API 키가 노출되면 어떻게 되나요?**
제3자가 본인 키로 Claude API를 마구 호출 → 본인에게 비용 청구. 즉시 console.anthropic.com에서 해당 키 폐기 + 새 키 발급. **절대 GitHub에 키를 커밋하지 마세요.** 항상 `.env` 파일에 두고 `.gitignore`에 `.env` 추가.

**② Claude가 헛소리(환각)를 해요**
(1) SYSTEM_PROMPT 마지막에 "위 정보에 없는 건 '잘 모르겠어요'라고만 답하세요" 추가. (2) `temperature`를 0.3으로 낮춰서 보수적으로 (Anthropic SDK 호출 시 `temperature: 0.3` 추가).

**③ Claude API 비용이 걱정돼요**
Sonnet 모델 기준 메시지 1건 약 1~3원. 월 1000건이어도 1~3천 원. 단, 무한 루프나 악성 사용자 대비: console.anthropic.com에서 월 사용 한도(Spend limit) 설정 + IP당 분당 호출 수 제한(rate limit) 추가.

**④ 디스코드 봇이 메시지에 응답 안 해요**
(1) 봇이 서버에 추가됐는지 확인. (2) Bot Permissions에 "Read Messages" + "Send Messages" 체크. (3) "MESSAGE CONTENT INTENT" 토글 ON. (4) 터미널의 `npm start` 프로세스가 살아 있는지 확인. (5) Discord Developer Portal에서 봇 재시작 (Reset Token).

**⑤ 카카오 webhook 등록 시 "URL 호출 실패"**
(1) URL이 HTTPS 인가? (2) URL이 공인 도메인인가? (로컬은 ngrok 필요) (3) 응답 시간이 5초 이내인가? Claude API가 느리면 타임아웃. `max_tokens`를 300으로 줄이거나 사전 캐싱 적용.

**⑥ 봇 응답이 너무 길거나 짧아요**
`max_tokens` 값을 조정. 카톡은 simpleText 한 번에 1000자가 최대. `max_tokens: 500` 정도가 안전. system prompt에 "3문장 이내로" 명시하면 더 짧게.
