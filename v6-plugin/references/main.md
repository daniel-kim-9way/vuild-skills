## EXPLAIN

### 플러그인이 정확히 뭐예요?

**플러그인(Plugin)**은 본인이 매일 쓰는 도구(=호스트 도구) 안에 끼워 넣는 작은 프로그램이에요. 콘센트에 꽂는 멀티탭이나, 카메라에 끼우는 렌즈를 떠올리면 비슷해요. 카메라 자체를 새로 사는 게 아니라, 카메라 앞에 렌즈 1개를 꽂으면 카메라가 갑자기 다른 일을 할 수 있죠. 플러그인도 마찬가지예요.

예를 들어 디자이너가 Figma에서 100개 컴포넌트를 한 번에 PNG로 export하고 싶어요. Figma 안에서 한 개씩 손으로 누르면 30분 걸려요. "한 번에 다 export" Figma 플러그인을 만들어 두면 30초로 끝나요.

### 왜 이번 lesson인가?

본인이 일주일 동안 PC 앞에서 반복하는 작업 중에는 반드시 1~2개의 "또 이거 하네" 작업이 있어요. 그 작업이 본인이 자주 쓰는 도구 안에서 일어난다면, 플러그인 1개로 끝낼 수 있어요. 한 번 만들어 두면 매주 5~12시간을 본인 손에 돌려 줘요.

이번 실습에서는 이렇게 진행해요:
1. 본인이 매일 반복하는 작업 1개 발견
2. 그 작업의 호스트 도구 1개 결정 (Claude Code / VS Code / Figma)
3. 호출 명령 + 입출력 정의
4. 스킬이 minimal 플러그인 파일 자동 생성
5. 본인 PC에 등록 + 1회 실행 확인

### 3가지 옵션 비교

| 옵션 | 만드는 데 걸리는 시간 | 호스트 도구가 누구에게 좋나? | 배포 난이도 |
|---|---|---|---|
| Claude Code 플러그인 (Skill) | 5분 | 터미널/코드 작업이 많은 사람 | 매우 쉬움 (`~/.claude/skills/` 폴더에 파일 두면 끝) |
| VS Code 확장 | 30분~1시간 | 코드 에디터에서 종일 작업하는 사람 | 중간 (`vsce package`로 `.vsix` 빌드) |
| Figma 플러그인 | 30분~1시간 | 디자이너·UI 작업 중심 | 중간 (개발자 모드에서 manifest 사이드로드) |

**처음이라면 Claude Code 플러그인부터.** 마크다운 파일 1개만 만들면 끝이라서 가장 빨라요. Claude Code 플러그인은 사실 "Skill"이라고 불리는 형태로, 본인이 지금 사용 중인 `/v6-plugin` 같은 것들이 전부 Skill이에요.

---

## EXECUTE

### Turn 1: 본인 반복 작업 발견하기

> "안녕하세요. 본인의 첫 플러그인을 만드는 시간이에요. 강의가 아니라 같이 손으로 만들어요."

> "먼저 질문 1개 — 본인이 **하루에 가장 많이 반복하는 작업 3가지**를 적어 주세요. 컴퓨터 안에서 하는 거든, 밖에서 하는 거든 상관없어요. 떠오르는 대로 짧게 적으면 돼요."

학습자 답변 예시 수용:
- "GitHub에서 PR 본문에 체크리스트 매번 손으로 적기"
- "회의 끝나고 노션에 회의록 정리하기"
- "Figma에서 컴포넌트 PNG로 export"
- "Slack에서 같은 답변 5번 복붙"

답변이 짧거나 막막해 보이면:
> "어제 PC 앞에서 한 일 5개를 그냥 쭉 적어 주세요. '또 이거 하네' 싶은 게 있으면 그게 정답이에요. 의심 없이 그걸 1순위로."

답변을 받으면 격려 + 다음 Turn:
> "좋아요. 이 중에서 1개를 골라서 자동화해 볼 거예요. 다음 질문으로 가요."

---

### Turn 2: 플러그인 후보로 좁히기

> "방금 적은 3개 중에 **컴퓨터 안에서** 하는 작업이 있나요? (즉, 어떤 앱이나 웹사이트 안에서 하는 작업)"

> "왜냐하면 플러그인은 호스트 도구 안에서만 살 수 있거든요. '아침에 커피 내리기'는 플러그인으로 못 만들어요. '노션에 회의록 정리'는 가능해요."

학습자가 1개를 고르면:
> "좋아요. 그 작업을 할 때 본인이 **가장 많이 머무는 도구**가 뭐예요? 예를 들어 'GitHub PR 체크리스트 작성'이라면 도구는 GitHub 웹사이트 또는 Claude Code(터미널). 'Figma 컴포넌트 export'라면 도구는 Figma 앱."

이 답이 다음 Turn의 호스트 결정 입력값이 돼요.

만약 학습자가 "잘 모르겠어요" 또는 "그냥 아무거나"라고 하면:
> "그럼 가장 단순한 걸로 시작해요. **'GitHub 또는 Claude Code 안에서 자주 하는 한 줄 작업'** 1개를 같이 골라 봐요. 예: '오늘 커밋 요약', 'PR 체크리스트 자동 생성'. 이런 거라면 Claude Code 플러그인 5분 안에 만들어요."

---

### Turn 3: 3가지 옵션 소개하기

> "본인이 고른 작업의 호스트 도구를 들었어요. 이제 어느 형태의 플러그인으로 만들지 결정해요. 3가지 옵션이 있어요:"

```
1. Claude Code 플러그인 (Skill 형태)
   → 본인 PC의 ~/.claude/skills/<이름>/SKILL.md 파일 1개만 만들면 끝.
   → 만드는 데 5분. 터미널/코드 작업이 호스트일 때 최고.
   → 호출은 Claude Code 안에서 /<이름>.

2. VS Code 확장
   → 4~6개 파일 (package.json, extension.js, README 등) 필요.
   → 만드는 데 30분~1시간. VS Code 에디터에서 종일 작업하는 사람용.
   → 호출은 VS Code 명령 팔레트(Cmd+Shift+P) 안에서.

3. Figma 플러그인
   → 4~5개 파일 (manifest.json, code.ts, ui.html 등) 필요.
   → 만드는 데 30분~1시간. 디자인 작업이 호스트일 때.
   → 호출은 Figma의 Plugins 메뉴.
```

> "본인 작업과 호스트 도구를 고려하면, **이 작업은 [추천 옵션]이 맞아요**. 같은 옵션으로 갈까요? 아니면 다른 옵션이 끌리나요?"

추천 로직 (학습자 답변 기반):
- 호스트가 "Claude Code", "터미널", "Cursor", "GitHub" → **Claude Code 플러그인**
- 호스트가 "VS Code", "Neovim", "에디터" → **VS Code 확장** (단, "Claude Code도 있다"면 Claude Code 추천 — 더 빠름)
- 호스트가 "Figma" → **Figma 플러그인**
- 그 외 (Notion, Slack, Chrome 등) → **Claude Code 플러그인** (가장 범용. 외부 API 호출로 노션/슬랙 모두 다룰 수 있음)

---

### Turn 4: 옵션 1개 확정 + 호출 명령 정하기

학습자가 옵션 1개를 결정했다고 가정.

> "좋아요. **[선택한 옵션]** 으로 가요."

> "이제 본인 플러그인의 **호출 명령(이름)** 을 정해요. 짧을수록 좋아요. 예시:"

옵션별 예시:
- Claude Code 플러그인: `/pr-checklist`, `/commit-summary`, `/notion-save`
- VS Code 확장: `Insert PR Checklist`, `Summarize Commit`, `Save to Notion`
- Figma 플러그인: `Export All as PNG`, `Replace Color`, `Generate Variants`

> "본인 작업에 맞춰 **이름 1개를 정해 주세요**. 짧고 외우기 쉬운 단어로."

학습자가 답하면:
> "좋아요, **[이름]** 로 갈게요."

> "마지막으로 입력·출력만 정해요. 이 플러그인은 무엇을 받아서(input) 무엇을 만들어요(output)?"

> "예: 입력 = 변경된 파일 목록. 출력 = 마크다운 PR 체크리스트 7항목."

학습자 답변을 받으면 다음 Turn으로.

---

### Turn 5: minimal 플러그인 구조 설명

> "이제 코드를 만들기 전에, **본인 [선택한 옵션] 플러그인의 minimal 구조** 만 빠르게 보여 드려요. 이걸 봐야 다음 Turn에서 받는 코드가 무슨 의미인지 이해돼요."

선택한 옵션에 따라 분기:

**Claude Code 플러그인 (Skill) 선택 시:**
> "Claude Code 플러그인은 마크다운 파일 **1개만** 있으면 끝이에요. 구조:"

```
~/.claude/skills/<본인-이름>/
└── SKILL.md     ← 이 파일 1개. 끝.
```

> "SKILL.md 안에는 (1) 이름과 설명을 적은 frontmatter, (2) 본문에 \"이 명령이 뭘 해야 하나\"를 자연어로 적어요. Claude가 그 본문을 읽고 알아서 실행해요. 코드를 직접 쓸 필요 없어요."

**VS Code 확장 선택 시:**
> "VS Code 확장은 5개 파일이 필요해요:"

```
my-vscode-ext/
├── package.json    ← 확장 메타데이터, 명령 이름 등록
├── extension.js    ← 실제 동작 코드
├── README.md       ← 설명
├── .vscodeignore   ← 패키징 제외 파일
└── icon.png        ← (선택) 마켓플레이스 아이콘
```

> "핵심은 `package.json`의 `contributes.commands` 부분에 본인 명령을 등록하고, `extension.js`의 `activate(context)` 함수 안에서 그 명령에 함수를 연결해요."

**Figma 플러그인 선택 시:**
> "Figma 플러그인은 4개 파일이 필요해요:"

```
my-figma-plugin/
├── manifest.json   ← 플러그인 메타데이터, 권한
├── code.ts         ← 메인 로직 (Figma 캔버스 조작)
├── ui.html         ← 사이드 패널 UI
└── README.md       ← 설명
```

> "Figma는 보안상 두 영역이 있어요. `code.ts`는 캔버스 데이터를 만지고, `ui.html`은 사용자가 보는 UI를 만져요. 두 영역은 `postMessage`로 통신해요."

> "구조 이해됐어요? 다음 Turn에서 본인용 파일을 자동 생성할게요."

---

### Turn 6: 자동 코드 생성

> "이제 본인이 입력한 정보를 바탕으로 **실제 파일을 만들어요**. 본인이 손으로 쓸 코드는 0줄이에요."

학습자 입력값을 정리해서 보여 줌:
```
- 호스트 도구: [Claude Code | VS Code | Figma]
- 플러그인 이름: [학습자가 정한 이름]
- 입력: [학습자가 정한 입력]
- 출력: [학습자가 정한 출력]
- 작업 한 줄 설명: [학습자의 반복 작업 설명]
```

이 정보로 **실제로 파일을 생성**한다.

#### Claude Code 플러그인 코드 템플릿

생성 위치: `~/.claude/skills/<이름>/SKILL.md` (학습자에게 본인 PC 경로 안내)

```markdown
---
name: <학습자가 정한 이름>
description: "<학습자가 정한 한 줄 설명>. Triggers: \"<이름>\", \"<관련 한국어 키워드>\""
---

# <학습자가 정한 이름>

## 목적
<학습자의 반복 작업 한 줄 설명>

## 사용법
이 스킬을 호출하면:
1. <입력>을 받는다
2. <중간 처리 단계 — 학습자 작업에 맞춰 자동 작성>
3. <출력>을 만든다

## 실행 단계
- Step 1: <Claude가 수행할 첫 단계>
- Step 2: <두 번째 단계>
- Step 3: <세 번째 단계>

## 출력 형식
<출력 예시 마크다운/JSON 등>
```

#### VS Code 확장 코드 템플릿

생성 위치: `vscode-ext-<이름>/` 폴더 (학습자 working directory 아래)

`package.json`:
```json
{
  "name": "<이름>",
  "displayName": "<이름>",
  "description": "<한 줄 설명>",
  "version": "0.0.1",
  "engines": { "vscode": "^1.85.0" },
  "main": "./extension.js",
  "activationEvents": ["onCommand:<이름>.run"],
  "contributes": {
    "commands": [
      { "command": "<이름>.run", "title": "<UI에 표시할 이름>" }
    ]
  }
}
```

`extension.js`:
```javascript
const vscode = require("vscode");

function activate(context) {
  const cmd = vscode.commands.registerCommand("<이름>.run", async () => {
    // <학습자 작업 로직 — 입력 받고 → 처리 → 출력>
    const input = await vscode.window.showInputBox({ prompt: "<입력 안내 문구>" });
    if (!input) return;

    // 처리 (필요 시 외부 API 호출 또는 텍스트 변환)
    const output = `<출력 형식 — 학습자 정의 기반>`;

    // 결과 표시
    await vscode.env.clipboard.writeText(output);
    vscode.window.showInformationMessage("<이름> 완료. 클립보드에 복사됨.");
  });
  context.subscriptions.push(cmd);
}

function deactivate() {}

module.exports = { activate, deactivate };
```

#### Figma 플러그인 코드 템플릿

생성 위치: `figma-plugin-<이름>/` 폴더

`manifest.json`:
```json
{
  "name": "<이름>",
  "id": "1234567890",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figma"],
  "permissions": []
}
```

`code.ts` (또는 `code.js`):
```javascript
figma.showUI(__html__, { width: 320, height: 240 });

figma.ui.onmessage = async (msg) => {
  if (msg.type === "run") {
    const selection = figma.currentPage.selection;
    // <학습자 작업에 맞춘 처리 — 선택한 노드 export, 색상 변경 등>
    figma.ui.postMessage({ type: "done", count: selection.length });
  }
};
```

`ui.html`:
```html
<style>body { font-family: system-ui; padding: 16px; }</style>
<h3><이름></h3>
<p><한 줄 설명></p>
<button id="run">실행하기</button>
<p id="result"></p>
<script>
  document.getElementById("run").onclick = () => {
    parent.postMessage({ pluginMessage: { type: "run" } }, "*");
  };
  window.onmessage = (e) => {
    const msg = e.data.pluginMessage;
    if (msg?.type === "done") {
      document.getElementById("result").innerText = `${msg.count}개 처리 완료`;
    }
  };
</script>
```

생성 완료 메시지:
> "파일이 만들어졌어요. 위치는 [경로]. 다음 Turn에서 본인 PC에 등록하고 1회 실행해요."

---

### Turn 7: 본인 PC에 등록 + 동작 확인

선택한 옵션에 따라 분기 가이드.

#### Claude Code 플러그인 등록

> "Claude Code 플러그인 등록은 가장 쉬워요. 3단계예요."

> "1. 본인 PC에서 `~/.claude/skills/` 폴더가 있는지 확인. (없으면 만드세요: `mkdir -p ~/.claude/skills`)"

> "2. 방금 만든 SKILL.md를 `~/.claude/skills/<본인-이름>/SKILL.md` 위치로 옮겨요. (또는 그 위치에 직접 저장)"

> "3. Claude Code 또는 Claude Desktop을 **재시작**. 새 채팅을 열고 `/`를 입력하면 자동완성에 본인 명령 `/<이름>`이 보여야 해요."

> "그 명령을 호출하고, 본인이 정의한 입력값을 넣어 보세요. 출력이 의도대로 나오면 성공이에요."

자동완성에 안 뜨면:
> "Claude를 완전히 종료(트레이/메뉴바 아이콘까지)하고 다시 켜 보세요. 그래도 안 보이면 SKILL.md 위치가 정확한지 확인. macOS면 `~/.claude/skills/<이름>/SKILL.md`, Windows면 `C:\\Users\\<유저명>\\.claude\\skills\\<이름>\\SKILL.md`."

#### VS Code 확장 등록 (사이드로드)

> "VS Code 확장은 4단계로 본인 PC에만 설치해요."

> "1. 터미널에서 확장 폴더로 이동: `cd vscode-ext-<이름>`"

> "2. 설치 도구 추가: `npm install -g @vscode/vsce` (1회만)"

> "3. 빌드: `vsce package` → `<이름>-0.0.1.vsix` 파일 생성됨"

> "4. VS Code 열기 → 좌측 확장 탭 → 우상단 `...` 메뉴 → `Install from VSIX...` → 방금 만든 `.vsix` 파일 선택"

> "설치 후 명령 팔레트(Cmd+Shift+P / Ctrl+Shift+P)를 열고 본인 명령 이름을 검색. 클릭해서 실행하세요."

오류 시:
> "오류 메시지가 뜨면 그 메시지를 그대로 저에게 보여 주세요. 보통 `package.json`의 `engines.vscode` 버전 또는 `activationEvents` 부분 문제예요."

#### Figma 플러그인 등록 (사이드로드)

> "Figma 플러그인은 5단계예요. **Figma 데스크톱 앱**이 있어야 해요. (브라우저는 안 됨)"

> "1. Figma 데스크톱 앱 실행 → 아무 파일이나 열기"

> "2. 메뉴: `Plugins` → `Development` → `Import plugin from manifest...`"

> "3. 본인 폴더의 `manifest.json` 선택"

> "4. 본인 계정에서만 보이는 플러그인이 됨 (공개 배포는 별도 절차)"

> "5. 다시 `Plugins` → `Development` → 본인 플러그인 이름 클릭. 사이드 패널이 뜨면 성공."

오류 시:
> "manifest.json 형식 오류면 Figma가 알려 줘요. 가장 흔한 건 `id` 필드가 비어 있는 경우. 임의의 숫자 문자열을 넣으세요. 또는 'main에 적힌 파일이 없다'는 오류면 `code.ts`를 `code.js`로 컴파일하거나 `code.ts`로 바꾸세요."

---

### Turn 8: 산출물 저장 + 다음 lesson 안내

> "방금 본인 PC에 첫 플러그인 1개를 띄웠어요. 다음 주에 같은 작업이 오면, 손이 아니라 1개 명령으로 끝내요. 매주 5~12시간 본인 손에 돌려 받아요."

> "오늘 만든 내용을 정리한 파일을 만들어 드려요. 다음 주에 다시 보고 호출 명령을 잊었거나, 친구한테 공유하고 싶을 때 이 파일을 보면 돼요."

`learn-outputs/ch6-1-plugin.md` 파일 생성:

```markdown
# Ch.6-1 — 내 첫 플러그인

## 호스트 도구
[Claude Code | VS Code | Figma]

## 플러그인 정보
- 이름: <학습자 이름>
- 호출 명령: <학습자 명령어>
- 한 줄 설명: <학습자 설명>
- 입력: <학습자 입력 정의>
- 출력: <학습자 출력 정의>

## 자동화한 반복 작업
<학습자가 적은 반복 작업 한 줄>

## 파일 위치
- 호스트: <학습자 PC 경로>
- 예: `~/.claude/skills/<이름>/SKILL.md`

## 호출 방법
1. <옵션별 호출 단계 1>
2. <옵션별 호출 단계 2>
3. <결과 확인 방법>

## 다음 주 재사용 체크리스트
- [ ] 같은 반복 작업이 다시 왔다
- [ ] 손으로 하지 말고 본인 플러그인을 호출했다
- [ ] 결과가 만족스러웠다 (아니면 SKILL.md/extension.js를 수정해서 개선)

## 다음 단계
- 다른 반복 작업 1개를 더 발견했다면, 같은 절차로 두 번째 플러그인 만들기
- 친구에게 공유하고 싶다면:
  - Claude Code: SKILL.md 파일을 그대로 보내기
  - VS Code: `.vsix` 파일을 보내기
  - Figma: 폴더 zip해서 보내기 (받는 사람도 사이드로드)

## 다음 lesson
- 6-2 자동화 (Slack/Notion/메일) — 도구들 사이를 자동으로 연결하기
```

마무리 메시지:
> "축하해요. 본인 첫 플러그인을 손에 쥐었어요."

> "잠깐, 방금 무슨 일이 있었는지 돌아볼게요:"

> "1. 본인이 매주 반복하는 작업 1개를 발견했어요."
> "2. 호스트 도구 1개를 결정했어요."
> "3. 코드를 한 줄도 직접 쓰지 않고, 자동으로 파일을 받았어요."
> "4. 본인 PC에 등록해서 실제로 1회 실행했어요."

> "이게 플러그인의 본질이에요. **본인 일을 1번 정의하면, 그 다음부터 영원히 자동.**"

> "다음 lesson은 6-2 자동화예요. 플러그인이 '도구 안에서 손을 줄이는' 거라면, 자동화는 '도구들 사이를 자동으로 연결'하는 거예요. 본인 SaaS에 가입이 들어오면 Slack 알림 + Notion DB 추가 + 환영 메일이 자동으로 흘러가요."

> "이어서 진행하려면 `/v7-automation` 또는 학습 사이트의 다음 lesson을 열어 주세요."

---

## 막히는 지점 — 미리 답

**① "어떤 작업을 자동화할지 모르겠어요"**
오늘 한 일을 5개만 적어 보세요. 그 중 "지난주에도 했네"가 있으면 그게 1순위 후보예요. 의심 없이 그걸로 가세요.

**② "/<본인 이름>" 자동완성이 안 떠요**
Claude Code/Desktop을 완전히 종료(트레이까지) 후 재시작. SKILL.md 위치가 정확한지 확인. 또는 직접 `/스킬이름`을 타이핑한 뒤 엔터를 누르고 "이 스킬을 사용해 줘"를 추가하면 동일하게 작동.

**③ Figma manifest.json이 어려워요**
"Figma plugin 공식 quickstart 문서대로 manifest 만들어 줘"라고 추가 요청. Figma 공식 문서: figma.com/plugin-docs/

**④ 만들어 놓고 다시 안 쓰게 돼요**
대부분 "사용 진입점이 멀어서"예요. 호출 명령어를 1단어로 짧게(`/pr` 처럼) 바꾸거나, Figma는 즐겨찾기에 등록하면 사용 빈도가 즉시 올라가요.

**⑤ VS Code `vsce package`가 실패해요**
가장 흔한 원인 2개: (1) `package.json`에 `publisher` 필드 빠짐 → `"publisher": "<본인 이름>"` 추가. (2) `README.md` 파일 없음 → 빈 README라도 1개 만들기.
