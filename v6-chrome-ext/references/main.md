## EXPLAIN

### 크롬 익스텐션 = 브라우저에 꽂는 작은 도구

**크롬 익스텐션(Chrome Extension)**은 크롬 브라우저 안에 들어가서 동작하는 작은 프로그램이에요. 본인이 평소 쓰는 광고 차단(AdBlock), 비밀번호 매니저(1Password), 번역기(DeepL) 같은 게 전부 익스텐션이에요. 주소창 우상단에 작은 아이콘이 뜨는 그것들이요.

### 4가지 능력

익스텐션은 크게 4가지 일을 할 수 있어요. 본인이 만들 익스텐션은 이 중 1~3개를 조합한 거예요.

| # | 능력 | 비유 | 예시 |
|---|---|---|---|
| 1 | **현재 페이지 내용 읽기** | 카메라가 눈앞 풍경을 찍는 것 | 본문 텍스트 추출, 가격 정보 스크랩 |
| 2 | **현재 페이지 수정** | 사진에 스티커 붙이는 것 | 광고 숨기기, 단어에 툴팁 추가 |
| 3 | **주소창 옆 팝업창 띄우기** | 현관에서 종 누르면 작은 창 열리는 것 | 번역 결과 표시, 옵션 메뉴 |
| 4 | **외부 API 호출** | 집 전화로 외부에 주문 거는 것 | Claude/Notion/Google Drive 호출 |

본인 워크플로우의 반복 작업이 이 4가지 안에 들어 있다면 익스텐션으로 자동화할 수 있어요.

### `manifest.json` = 익스텐션의 이름표 + 권한 신청서

모든 크롬 익스텐션은 `manifest.json` 파일 1개로 시작해요. 이 파일은 크롬에게 **"내 익스텐션 이름은 뭐고, 어떤 권한이 필요하고(예: 모든 페이지 읽기), 어떤 파일을 실행할 거다"**를 알려 주는 약속이에요.

만약 manifest.json이 없거나 잘못되어 있으면, 크롬은 익스텐션을 아예 로드하지 않아요. 신분증 없이 회사 출입하려는 거랑 같아요.

가장 단순한 manifest 예시:

```json
{
  "manifest_version": 3,
  "name": "내 페이지 요약 → Notion",
  "version": "0.1.0",
  "description": "지금 보고 있는 페이지를 요약해서 Notion에 저장",
  "permissions": ["activeTab", "storage"],
  "host_permissions": ["https://api.anthropic.com/*"],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  }
}
```

각 필드 의미:
- `manifest_version`: 3 (현재 표준. 2024년 기준)
- `permissions`: 권한 신청. `activeTab`은 "지금 본 탭만 읽을 수 있게 해 줘", `storage`는 "본인 PC에 작은 데이터 저장하게 해 줘"
- `host_permissions`: 외부 API 도메인에 요청 보낼 수 있게 해 줘
- `action.default_popup`: 주소창 옆 아이콘을 클릭했을 때 뜨는 작은 HTML 페이지

권한은 **최소로** 신청하세요. 사용자도 본인도 더 안전해요.

---

## EXECUTE

### Turn 1: 본인 브라우저 반복 작업 발견하기

> "안녕하세요. 본인의 첫 크롬 익스텐션을 만드는 시간이에요. 강의가 아니라 같이 손으로 만들어요."

> "먼저 질문 1개 — 본인이 **브라우저에서 자주 하는 반복 작업 3가지**를 적어 주세요. 짧게 적으면 돼요."

학습자 답변 예시 수용:
- "긴 영어 기사를 한국어 3줄 요약해서 Notion에 저장"
- "모르는 영단어 더블클릭하면 의미 보기"
- "경쟁 SaaS 가격 페이지 매주 모니터링"
- "PDF 페이지 → 마크다운 변환"
- "GitHub 이슈 본문을 한국어로 번역"

답변이 막막해 보이면:
> "브라우저에서 같은 동작을 1주에 5번 이상 하는 게 있나요? 그게 후보예요. 의심 없이 그걸 1순위로."

답변을 받으면:
> "좋아요. 다음 Turn에서 이 중 1개를 골라요."

---

### Turn 2: 1개 골라서 한 줄 정의

> "방금 적은 3개 중에 **1개**만 골라요. 처음이니까 가장 단순한 거로 시작해요."

> "예를 들어 '긴 기사 요약 + Notion 저장'이라면 처음엔 'Notion 저장'은 빼고 '긴 기사 요약'만 만들어요. 절반이라도 살아 움직이면 다음에 확장하면 돼요."

학습자가 1개를 고르면:
> "좋아요. 그 익스텐션을 **한 줄로** 정의해 주세요. 다른 사람한테 설명한다면? 예: '지금 페이지 본문을 한국어 3줄로 요약해서 팝업에 보여 주는 익스텐션'."

학습자 한 줄 정의를 받음. 이게 manifest.json의 `description` 필드가 됨.

> "다음 Turn에서 이 익스텐션이 **4가지 능력 중 어디에 해당하는지** 같이 분류해요."

---

### Turn 3: manifest.json 이해 + 4가지 능력 분류

> "본인 익스텐션이 4가지 능력 중 어디 어디 쓰는지 정해요. 이게 manifest.json의 권한을 결정해요."

```
1. 현재 페이지 내용 읽기 (예: 본문 텍스트, URL, 메타데이터)
2. 현재 페이지 수정 (예: 단어 강조, 광고 숨기기, 툴팁 추가)
3. 주소창 옆 팝업창 띄우기 (예: 번역 결과, 옵션 메뉴, 결과 표시)
4. 외부 API 호출 (예: Claude, Notion, Google Drive, 본인 SaaS)
```

> "본인 익스텐션은 위 중 어느 항목들이 필요해요? (1개 또는 여러 개) 예시:"

```
"긴 기사 요약 → 팝업" → 1번 + 3번 + 4번 (Claude API)
"단어 더블클릭 의미 보기" → 1번 + 2번 + 4번 (Claude API)
"가격 페이지 모니터링" → 1번 + 4번 (본인 SaaS API)
"GitHub 이슈 한국어 번역" → 1번 + 2번 + 4번 (Claude API)
```

> "본인 거를 분류해서 알려 주세요."

학습자 답변을 받으면, 그에 맞는 권한 자동 결정:
- 1번 (페이지 읽기) → `permissions: ["activeTab"]` + `host_permissions` 또는 `content_scripts`
- 2번 (페이지 수정) → `content_scripts`
- 3번 (팝업) → `action.default_popup`
- 4번 (외부 API) → `host_permissions: ["https://api.도메인.com/*"]`

> "권한은 **최소로** 갈게요. `activeTab`은 사용자가 아이콘을 누른 탭에만 적용돼서 안전해요. 모든 페이지에 항상 접근하는 `<all_urls>`는 필요할 때만 써요."

---

### Turn 4: minimal manifest.json 자동 생성

학습자의 정의 + 4가지 능력 분류로 `manifest.json` 생성.

생성 위치: `chrome-ext-<학습자가 정한 짧은 이름>/manifest.json`

```json
{
  "manifest_version": 3,
  "name": "<학습자 한 줄 정의>",
  "version": "0.1.0",
  "description": "<학습자 한 줄 정의>",
  "permissions": ["activeTab"<학습자 능력에 따라 추가>],
  "host_permissions": [<학습자가 호출할 외부 API 도메인 목록>],
  "action": {
    "default_popup": "popup.html",
    "default_title": "<학습자 익스텐션 짧은 이름>"
  }
}
```

설명:
- `name`은 사용자가 보는 이름. 짧고 명확하게.
- `version`은 본인 임의. 시작은 0.1.0이 표준.
- `permissions`는 4가지 능력에서 1, 2번을 쓸 때 `activeTab` 또는 `scripting` 등 추가.
- `host_permissions`는 외부 API 호출 도메인. Claude는 `https://api.anthropic.com/*`, Notion은 `https://api.notion.com/*`.

> "이 manifest는 학습자 본인용으로 minimal 형태예요. 더 복잡한 기능이 필요해지면 나중에 추가."

---

### Turn 5: popup HTML/JS 작성

> "다음은 사용자가 아이콘 누르면 뜨는 작은 화면(popup)을 만들어요."

> "popup은 그냥 작은 HTML 파일이에요. CSS, JavaScript도 평소 웹페이지처럼 쓸 수 있어요. 단, 보안상 `<script>`는 인라인 금지(외부 파일로만)예요."

생성: `popup.html`

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      body { width: 320px; padding: 16px; font-family: system-ui; font-size: 14px; }
      h3 { margin: 0 0 12px; font-size: 16px; }
      button { width: 100%; padding: 10px; background: #2563eb; color: white;
               border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }
      button:hover { background: #1d4ed8; }
      #result { margin-top: 12px; padding: 12px; background: #f3f4f6;
                border-radius: 6px; min-height: 40px; line-height: 1.5;
                white-space: pre-wrap; }
      .loading { color: #6b7280; font-style: italic; }
    </style>
  </head>
  <body>
    <h3><학습자 익스텐션 이름></h3>
    <button id="run"><학습자가 정한 액션 단어 — 예: '요약하기'></button>
    <div id="result"></div>
    <script src="popup.js"></script>
  </body>
</html>
```

생성: `popup.js`

```javascript
const runBtn = document.getElementById("run");
const resultEl = document.getElementById("result");

runBtn.addEventListener("click", async () => {
  resultEl.className = "loading";
  resultEl.innerText = "처리 중...";
  runBtn.disabled = true;

  try {
    // 1. 현재 탭의 본문 텍스트 가져오기 (능력 1번)
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const [{ result: pageText }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => document.body.innerText.slice(0, 5000),
    });

    // 2. <학습자 작업에 맞춘 처리 — Claude API 호출 등 (능력 4번)>
    // 아래는 "한국어 3줄 요약" 예시. 학습자 작업에 맞춰 prompt 변경.
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": "<API_KEY_PLACEHOLDER>",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-5",
        max_tokens: 300,
        messages: [
          { role: "user", content: "다음 글을 한국어 3줄로 요약: " + pageText },
        ],
      }),
    });
    if (!r.ok) throw new Error("API " + r.status);
    const j = await r.json();
    const text = j.content?.[0]?.text || "(응답 비어 있음)";

    // 3. 결과 표시 (능력 3번)
    resultEl.className = "";
    resultEl.innerText = text;
  } catch (e) {
    resultEl.className = "";
    resultEl.innerText = "오류: " + e.message;
  } finally {
    runBtn.disabled = false;
  }
});
```

생성: 1x1 임시 `icon.png` (placeholder. 학습자가 나중에 교체)

학습자에게 안내:
> "icon.png는 일단 placeholder로 둘게요. 나중에 본인 디자인으로 바꾸세요. 16x16, 48x48, 128x128 사이즈가 표준이에요. Figma나 https://favicon.io 같은 데서 5분이면 만들어요."

---

### Turn 6: Claude API 키 연동 (선택 — 학습자 익스텐션이 외부 API 쓸 때만)

> "본인 익스텐션이 Claude API를 호출한다면, API 키가 필요해요."

학습자가 v6-chatbot에서 키를 이미 발급했다면:
> "v6-chatbot에서 발급한 키 그대로 쓸 수 있어요. 같은 키로 양쪽 호출 가능해요."

발급 안 했다면:
> "https://console.anthropic.com → API Keys → Create Key → 발급된 sk-ant-... 키 복사. (자세한 절차는 v6-chatbot Turn 3 참고)"

> "**⚠️ 중요한 보안 주의:**"

> "익스텐션 코드는 사용자 PC에 그대로 풀려서 키가 노출돼요. 다음 두 가지 시나리오가 있어요:"

```
A) 본인만 쓰는 사이드로드 (오늘 우리가 하는 것)
   → API 키를 popup.js에 직접 넣어도 OK
   → 본인 PC 안에서만 사는 코드라서

B) 친구·공개 배포
   → 절대 키를 코드에 넣으면 안 됨
   → 본인 SaaS 백엔드를 사이에 두고 호출 (browser → 본인 백엔드 → Claude API)
```

> "오늘은 A 케이스로 진행해요. popup.js의 `<API_KEY_PLACEHOLDER>` 부분을 본인 키(`sk-ant-...`)로 바꾸세요."

> "✅ 그래도 GitHub 같은 공개 저장소에는 절대 올리지 마세요. 본인 PC 안에만 두세요."

학습자가 키를 채웠다고 확인하면 다음 Turn으로.

대안 — `chrome.storage.local`에 키 저장:
> "키를 코드에 직접 박는 게 싫다면, `chrome.storage.local` 에 저장하고 popup.js가 읽게 할 수도 있어요. 약간 더 안전해요. 원하시면 그 형태로도 만들어 드려요."

---

### Turn 7: chrome://extensions 사이드로드 + 실제 테스트

> "이제 본인 크롬에 익스텐션을 설치해요. **5단계**예요."

```
1. 크롬 주소창에 chrome://extensions 입력 → 엔터
2. 페이지 우상단의 "개발자 모드" 토글을 ON (오른쪽으로 밀기)
3. 좌상단에 새로 나타난 "압축 해제된 확장 프로그램 로드" 버튼 클릭
4. 본인 익스텐션 폴더(chrome-ext-<이름>) 선택
5. 익스텐션 카드가 추가되고, 주소창 우상단에 본인 아이콘이 나타남
```

> "주소창 우상단에 본인 아이콘이 안 보이면? 크롬 메뉴 우상단의 퍼즐 모양 아이콘을 누르고, 본인 익스텐션 옆의 핀(pin) 아이콘을 클릭하세요. 항상 보이게 고정돼요."

> "이제 본인이 자주 가는 페이지(블로그·뉴스·문서)로 이동 → 익스텐션 아이콘 클릭 → 팝업이 뜨고 → 액션 버튼 누르기 → 결과가 뜨면 성공!"

확인 사항:
- ✅ 아이콘이 주소창 옆에 떠 있음
- ✅ 클릭하면 팝업이 뜸
- ✅ 액션 버튼 누르면 처리되고 결과가 표시됨
- ✅ 본인 작업 의도대로 동작함

#### 트러블슈팅

> "오류가 났다면? `chrome://extensions` 본인 익스텐션 카드 우하단에 **'오류'** 버튼이 떠 있을 거예요. 클릭하면 어떤 줄에서 문제가 났는지 표시돼요. 그 메시지를 저에게 보여 주시면 같이 고쳐요."

자주 일어나는 오류:
- **"Manifest is not valid JSON"**: manifest.json의 콤마/괄호 문법 오류. JSON 검증 사이트(jsonlint.com)에 붙여넣어서 확인.
- **"Cannot read properties of undefined"**: popup.js에서 DOM 요소를 찾기 전에 접근. 스크립트 위치를 `</body>` 직전으로.
- **"Failed to fetch" 또는 CORS 오류**: `host_permissions`에 호출할 도메인 추가. `"host_permissions": ["https://api.anthropic.com/*"]`. 그래도 안 되면 background service worker로 옮기기 (스킬이 알아서 변환).
- **API 401 Unauthorized**: API 키가 잘못됐거나 placeholder 그대로. `<API_KEY_PLACEHOLDER>` 부분을 실제 키로 교체.
- **"Service worker registration failed"**: manifest.json에 `background.service_worker`를 잘못 적었을 때. 처음 익스텐션엔 이 필드 자체를 빼세요.

---

### Turn 8: 산출물 저장 + 다음 lesson 안내

> "본인 첫 크롬 익스텐션이 살아 움직여요. 매일 가는 페이지에서 1번 클릭으로 본인이 자주 하던 작업이 끝나요."

> "오늘 만든 내용을 정리한 파일을 만들어 드려요."

`learn-outputs/ch6-4-chrome-ext.md` 생성:

```markdown
# Ch.6-4 — 내 첫 크롬 익스텐션

## 익스텐션 한 줄 정의
[학습자 한 줄 정의]

## 자동화한 반복 작업
[학습자가 적은 반복 작업]

## 사용한 4가지 능력
- [✓/✗] 1. 현재 페이지 내용 읽기
- [✓/✗] 2. 현재 페이지 수정
- [✓/✗] 3. 주소창 옆 팝업
- [✓/✗] 4. 외부 API 호출 (어디? Claude/Notion/...)

## 권한 (manifest.json)
- permissions: [목록]
- host_permissions: [목록]

## 폴더 위치
chrome-ext-<이름>/
├── manifest.json
├── popup.html
├── popup.js
└── icon.png

## API 키 보관 (해당 시)
- 위치: popup.js 안 (본인만 쓰는 사이드로드용)
- ⚠ 절대 GitHub 같은 공개 저장소에 올리지 말 것

## 사이드로드 절차 (본인 PC)
1. chrome://extensions → 개발자 모드 ON
2. "압축 해제된 확장 프로그램 로드" → 폴더 선택
3. 주소창 우상단에 아이콘이 뜨면 핀(pin) 고정

## 테스트 결과
- 테스트한 페이지: [URL 또는 사이트 이름]
- 결과: [성공 / 실패 + 메시지]
- 동작 시간: [초]

## 친구에게 공유하는 방법
1. 폴더를 zip 압축
2. 친구에게 zip 전송
3. 친구도 chrome://extensions → 개발자 모드 → "압축 해제된 확장 프로그램 로드"로 본인 폴더 선택
4. (Chrome Web Store 정식 등록은 1회 $5 + 검수 1~3일. 친구 5명까지는 zip 공유로 충분)

## 다음 단계 아이디어
- [ ] icon.png를 본인 디자인으로 교체 (favicon.io에서 5분)
- [ ] background script로 정기 실행 추가 (예: 매시간 모니터링)
- [ ] options.html 추가해서 사용자 설정 가능하게
- [ ] (공개 시) 본인 SaaS 백엔드 거쳐서 API 키 보안 강화

## 다음 lesson
- 6-5 AI 비서 만들기 (RAG) — 익스텐션이 "브라우저 안의 작은 도우미"라면, AI 비서는 "본인 자료 전부를 base로 한 큰 도우미"
```

마무리:
> "본인이 매일 가는 페이지에 본인 도구가 1개 박혀 있어요. 1번 클릭으로 30분 작업이 30초로 끝나요."

> "잠깐 정리:"
> "1. 본인 브라우저 반복 작업 1개를 발견했어요."
> "2. 4가지 능력 중 어디에 해당하는지 분류했어요."
> "3. manifest.json + popup.html + popup.js 4개 파일을 받았어요."
> "4. 본인 크롬에 사이드로드해서 실제로 동작하는 걸 봤어요."

> "이게 익스텐션의 본질이에요. **본인이 자주 가는 페이지에 본인 도구를 박는다.**"

> "다음 lesson은 6-5 AI 비서예요. 이번엔 '본인 자료 전체'를 base로 한 큰 도우미를 만들어요. 본인 노트·문서·블로그를 컨텍스트로 한 개인 AI예요."

> "이어서 진행하려면 `/v6-ai-assistant` 또는 학습 사이트의 다음 lesson을 열어 주세요."

---

## 막히는 지점 — 미리 답

**① "압축 해제된 확장 프로그램 로드"가 안 보여요**
우상단 "개발자 모드" 토글이 ON 되어 있는지 확인. OFF면 좌상단 버튼이 숨겨져 있어요.

**② manifest 오류 메시지가 떠요**
`chrome://extensions` 본인 익스텐션 카드 우하단의 "오류" 버튼 클릭 → 어떤 줄에서 문제가 났는지 표시. 대부분 JSON 문법 오류(콤마/괄호) 또는 manifest_version이 2(구버전)인 경우. 3으로 바꾸세요.

**③ 외부 API 호출이 CORS로 막혀요**
`host_permissions`에 호출할 도메인 추가 + 그래도 막히면 Service Worker(`background.js`)에서 호출하면 CORS 우회. 스킬이 변환 코드를 만들어 줘요.

**④ 친구에게 공유하고 싶어요**
(1) 폴더 zip해서 보내고 친구도 "압축 해제된" 모드로 설치(사이드로드). (2) Chrome Web Store 등록 (1회 $5 + 검수 1~3일). 처음에는 (1)로 충분.

**⑤ 익스텐션이 페이지 로드되자마자 자동 실행되게 하고 싶어요**
manifest.json에 `content_scripts`를 추가하고, `matches: ["<특정 사이트 패턴>"]`로 적용 사이트를 좁히세요. 그러면 사용자가 아이콘 안 눌러도 자동 실행. 단, 권한이 강해지므로 정말 필요할 때만.

**⑥ 팝업 크기가 너무 작아요/잘려 보여요**
popup.html의 `<body>` style에서 `width`를 늘리세요(최대 800px 권장). `min-height`도 같이 지정. 팝업은 스크롤이 자연스럽게 생기지만, 처음부터 잘 맞추는 게 좋아요.

**⑦ 코드 수정 후 새로고침이 안 돼요**
`chrome://extensions`에서 본인 익스텐션 카드의 새로고침(↻) 버튼을 눌러야 해요. 코드만 저장하면 반영 안 됨. 또는 Cmd+R/Ctrl+R로 chrome://extensions 페이지 자체를 새로고침해도 돼요.
