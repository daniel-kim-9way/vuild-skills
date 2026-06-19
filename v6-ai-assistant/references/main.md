## EXPLAIN

### RAG가 정확히 뭐예요?

**RAG**는 **Retrieval-Augmented Generation**의 줄임말이에요. 한국어로 풀면 "**검색 보강 생성**", 더 쉽게 풀면 "**AI가 답하기 전에 본인 자료를 먼저 찾아보고 답하는 방식**"이에요.

### 비유 — 도서관 사서

일반 ChatGPT/Claude는 **모든 책을 통째로 외운 천재**예요. 단, 본인이 작년에 쓴 일기장은 못 외웠어요. 본인 책장 안의 책은 아무것도 몰라요.

RAG는 그 천재 옆에 **본인 책장 전담 사서 1명**을 두는 거예요.
- 본인이 "지난주 결정사항 요약해 줘"라고 물어요.
- 사서가 본인 책장(노트·문서)에서 "지난주" 키워드와 비슷한 책 3~5권을 빠르게 뽑아 와요.
- 그 책들을 천재 옆에 펼쳐 두면, 천재가 그 자료를 보면서 정확하게 답해요.

이게 RAG예요. 일반 LLM에 "검색" 단계를 1개 끼워 넣은 패턴.

### 왜 RAG가 필요해요?

일반 ChatGPT/Claude는 학습 데이터와 본인 질문만 보고 답해요. 본인 독서 노트 1200개, 본인 블로그 500개, 본인 회의록 200개에 대해서는 아무것도 몰라요. 본인이 매번 "내가 X 책에서 이렇게 적었어, 그리고 Y 회의에서 이런 결정을 했어..."를 처음부터 알려 줘야 해요.

RAG는 이 비효율을 해결해요. 한 번 셋업하면 그 다음부터는 본인이 질문만 던져요. 자료 검색은 사서(RAG 시스템)가 알아서 해요.

### RAG 부품 3가지

| 부품 | 역할 | 대표 도구 |
|---|---|---|
| 임베딩 모델 | 텍스트를 "의미 좌표(숫자 벡터)"로 변환. 비슷한 의미는 비슷한 좌표. | OpenAI text-embedding-3-small / Voyage AI |
| Vector DB | 의미 좌표를 저장 + 검색(가장 가까운 N개 찾기). | ChromaDB(로컬·무료) / Pinecone(클라우드) |
| 생성 LLM | 검색된 문서 + 본인 질문을 받아 최종 답변 작성. | Claude Sonnet/Opus (한국어 최강) |

### 자료가 100건 미만이면 RAG 안 써도 돼요 (긴 컨텍스트 모드)

Claude Sonnet/Opus는 컨텍스트 200K 토큰(약 한국어 100,000자, 단행본 약 1권)을 한 번에 받을 수 있어요. 본인 자료 전체가 그 안에 들어간다면 그냥 system prompt에 통째로 넣고 끝이에요. Vector DB 불필요.

이걸 "**긴 컨텍스트 RAG**"라고 불러요. 입문 추천이에요. 코드 30줄로 끝나요.

### 두 가지 모드 비교

| 항목 | 긴 컨텍스트 모드 | Vector DB 모드 |
|---|---|---|
| 자료 양 | 100건 미만 또는 ~10만자 이내 | 100건 이상 또는 긴 문서 |
| 셋업 시간 | 30분 | 2~3시간 |
| 운영비/월 | $5~$15 (Claude만) | $5~$15 (Claude) + $0~$20 (Pinecone, 또는 ChromaDB는 무료) |
| 자료 갱신 | 매번 자동 (코드가 폴더 다시 읽음) | 새 자료만 임베딩 추가 |
| 검색 정확도 | 매번 전체 자료 보므로 100% | 검색된 5개 자료에 한정 |
| 응답 시간 | 느림 (컨텍스트 큼) | 빠름 |

> 처음이면 **긴 컨텍스트 모드**부터. 자료가 늘어나서 한계 오면 그때 Vector DB로 옮기세요. 같은 system prompt를 그대로 재사용해요.

---

## EXECUTE

### Turn 1: 본인 자료 파악

> "안녕하세요. 본인 개인 AI 비서를 만드는 시간이에요. 본인이 그 동안 쌓아 온 자료를 base로 한 AI를 만들어요."

> "먼저 — 본인이 가지고 있는 자료가 뭐예요? 떠오르는 대로 적어 주세요."

예시 카테고리 안내:
- Notion 노트
- Obsidian / Bear / Apple Notes 노트
- Google Docs / Word 문서
- 본인 블로그 글 (Velog/티스토리/미디엄)
- 회의록 / 인터뷰 녹취록
- PDF 책 요약 / 독서 노트
- Slack / Discord 대화 export
- 이메일 export

학습자 답변을 받으면:
> "좋아요. 그 중에서 **AI 비서가 base로 삼을 자료**를 1~2개 카테고리로 좁혀요. 너무 다양한 자료를 한 번에 섞으면 정확도가 떨어져요."

> "예: '독서 노트만' 또는 '본인 블로그만' 또는 '본인 회의록만'."

좁힌 결과 + **자료의 양**을 정확히 물어 봐요:
> "그 카테고리 자료가 **몇 건** 정도예요? 대략. 그리고 평균 길이(짧은 메모 / 긴 글)도 알려 주세요."

답변 예시:
- "Notion 독서 노트 1200건, 평균 300자"
- "본인 블로그 500편, 평균 2000자"
- "회의록 200건, 평균 1500자"

이 정보가 다음 Turn(모드 결정)의 핵심 입력이 돼요.

---

### Turn 2: RAG가 뭔지 설명

> "본격적으로 들어가기 전에 — RAG가 뭔지 한 번 더 짚어요. 이게 머릿속에 잡혀야 다음 단계가 자연스러워요."

> "RAG는 **AI에게 답을 물어볼 때, 답하기 전에 본인 자료를 먼저 찾아보고 답하게 하는 방식**이에요."

> "비유 한 번 더 — 본인이 친구한테 '내가 작년에 추천한 책 중에 자기개발서 3권 뭐였지?'라고 물어요. 친구가 그걸 어떻게 알겠어요? 본인 독서 노트를 먼저 보고 답해야 알죠. RAG가 정확히 그 흐름이에요."

> "일반 ChatGPT에 같은 질문 하면 — '저는 당신 데이터에 접근할 수 없습니다'라고 답해요. 또는 더 위험한 건 **그럴듯하게 지어낸 답** 을 줘요. 본인이 적은 적도 없는 책 제목을 추천한다거나."

> "RAG는 이 두 문제를 모두 해결해요. **본인 자료 안에서만** 답해요."

> "다음 질문 — 본인은 이 AI 비서에게 **무엇을 물어보고 싶어요?** 예시:"

```
- "지난주 회의 핵심 결정사항 3개"
- "내가 작년에 추천한 자기개발서 중 평점 높았던 거"
- "X 클라이언트 관련 모든 메모를 요약"
- "내 블로그 중 SEO 잘된 글 패턴"
- "내가 올해 가장 자주 쓴 단어 / 주제"
```

> "본인 비서에 묻고 싶은 질문 5개를 적어 주세요. 이 5개가 나중에 정확도 검증에도 쓰여요."

---

### Turn 3: 도구 선택 (긴 컨텍스트 vs Vector DB)

학습자가 적은 자료 양/평균 길이로 모드 추천:

자료 총량 계산:
- 자료 건수 × 평균 글자수 = 총 글자수
- 총 글자수 < 100,000 (10만자) → **긴 컨텍스트 모드** 가능
- 총 글자수 ≥ 100,000 → **Vector DB 모드** 권장

> "본인 자료를 합치면 약 **[총 글자수]자** 예요. 이걸 기준으로:"

학습자 자료가 10만자 미만:
> "**긴 컨텍스트 모드** 추천이에요. 셋업 30분, 코드 30줄로 끝나요. 제가 추천하는 길로 갈게요."

학습자 자료가 10만자 이상:
> "**Vector DB 모드** 추천이에요. 셋업 2~3시간, 하지만 한 번 만들어 두면 자료 100만 건까지도 돌아가요. 어디까지 갈래요?"

```
A) 일단 작게 시작 — 가장 중요한 자료 50~100건만 골라서 긴 컨텍스트로 빠르게
B) 본격적으로 — Vector DB(ChromaDB) 셋업해서 전체 자료 처리
```

> "처음이라면 **A) 작게 시작** 추천이에요. 실제로 동작하는 비서를 빨리 만들고, 나중에 확장하기. 어느 쪽으로 갈까요?"

학습자 응답에 따라 분기. **긴 컨텍스트 모드**로 가는 경로를 default로 하고, Vector DB는 advanced 케이스로 안내.

---

### Turn 4: 셋업 가이드 (긴 컨텍스트 모드 / Vector DB 모드)

#### 긴 컨텍스트 모드 셋업

> "긴 컨텍스트 모드는 단순해요. 3가지만 있으면 돼요."

```
1. Anthropic API 키 (v6-chatbot에서 발급한 것 재사용)
2. Ruby 또는 Node.js (선택)
3. 본인 자료를 마크다운/텍스트 파일로 한 폴더에 모음
```

> "Ruby가 익숙하면 Ruby로, JavaScript가 익숙하면 Node로 갈게요. 어느 거? (모르면 Ruby 추천 — 본인 Rails SaaS에 합치기 쉬움)"

학습자 응답을 받음.

#### Vector DB 모드 셋업

> "Vector DB는 ChromaDB(로컬, 무료) 또는 Pinecone(클라우드, 무료 티어 있음) 중 선택. 처음이면 ChromaDB 추천. SQLite처럼 파일 1개로 동작하고 별도 서버 불필요."

```
1. Anthropic API 키
2. OpenAI API 키 (임베딩용. text-embedding-3-small 사용. 1만 건 임베딩 약 $0.20)
3. Python 3.10+ 또는 Node.js
4. 본인 자료를 한 폴더에 모음
```

> "ChromaDB는 Python에서 가장 안정적이에요. Python 추천. 익숙하지 않다면 stage 1로 일단 긴 컨텍스트로 가고, 나중에 마이그레이션하는 길도 OK."

이 Turn 완료 후 학습자 자료 추출 단계로.

---

### Turn 5: 본인 자료를 비서에 주입

#### 긴 컨텍스트 모드 — 자료 추출 + 코드

자료 추출 가이드 (자료 위치별):

**Notion에서 export:**
```
1. Notion 좌측 페이지 우클릭 → "Export"
2. 형식: Markdown & CSV
3. Include subpages: ON
4. Export → zip 다운로드 → 압축 해제
5. 압축 푼 폴더 안의 .md 파일들이 본인 자료
```

**Obsidian:**
```
이미 마크다운이라 별도 export 불필요. Vault 폴더 그대로.
```

**Google Docs:**
```
1. Google Drive에서 자료 폴더 우클릭 → "Download"
2. zip 다운로드
3. .docx 파일들 → pandoc으로 .md 변환 (또는 수동 복붙)
   pandoc input.docx -o output.md
```

**블로그 글:**
```
티스토리: 백업 도구 사용 / Velog: 본인 글 페이지 수동 복사
또는 RSS feed → 마크다운 변환 스크립트 (스킬이 만들어 줌)
```

> "본인 자료를 `data/notes/` 폴더 아래에 .md 파일들로 모아요. 한 자료당 한 파일."

자료 모은 후 코드 자동 생성:

`assistant.rb` (Ruby):
```ruby
require "http"
require "dotenv/load"

class PersonalAssistant
  NOTES_DIR = "data/notes"

  def initialize
    files = Dir.glob("#{NOTES_DIR}/*.md")
    @notes = files.map { |f|
      "## 자료: #{File.basename(f, '.md')}\n#{File.read(f)}"
    }.join("\n\n---\n\n")
    puts "[load] #{files.size}개 자료 로드, 총 #{@notes.length}자"
  end

  def ask(question)
    res = HTTP.headers(
      "x-api-key" => ENV.fetch("ANTHROPIC_API_KEY"),
      "anthropic-version" => "2023-06-01",
      "content-type" => "application/json"
    ).post("https://api.anthropic.com/v1/messages", json: {
      model: "claude-sonnet-4-5",
      max_tokens: 1500,
      system: <<~SYS,
        당신은 사용자의 개인 노트를 base로 답하는 AI 비서입니다.
        아래는 사용자의 자료 모음입니다. 이 자료에서만 근거를 찾아 답하세요.
        근거가 없으면 "확실치 않습니다, 자료에서 찾지 못했어요"라고 답하세요.
        답변 마지막에 "(출처: 자료 X, Y)" 형태로 어느 자료를 참조했는지 표시.

        === 사용자 자료 ===
        #{@notes}
      SYS
      messages: [{ role: "user", content: question }]
    })
    res.parse.dig("content", 0, "text")
  end
end

# 사용 예
assistant = PersonalAssistant.new
puts assistant.ask(ARGV.join(" "))
```

실행:
```
bundle add http dotenv
ruby assistant.rb "지난주 결정사항 요약"
```

`assistant.js` (Node.js):
```javascript
import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import Anthropic from "@anthropic-ai/sdk";

const NOTES_DIR = "data/notes";
const anthropic = new Anthropic();

function loadNotes() {
  const files = fs.readdirSync(NOTES_DIR).filter(f => f.endsWith(".md"));
  const notes = files.map(f => {
    const content = fs.readFileSync(path.join(NOTES_DIR, f), "utf8");
    return `## 자료: ${path.basename(f, ".md")}\n${content}`;
  }).join("\n\n---\n\n");
  console.log(`[load] ${files.length}개 자료, 총 ${notes.length}자`);
  return notes;
}

const notes = loadNotes();

async function ask(question) {
  const res = await anthropic.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 1500,
    system: `당신은 사용자의 개인 노트를 base로 답하는 AI 비서입니다.
아래는 사용자의 자료 모음입니다. 이 자료에서만 근거를 찾아 답하세요.
근거가 없으면 "확실치 않습니다, 자료에서 찾지 못했어요"라고 답하세요.
답변 마지막에 "(출처: 자료 X, Y)" 형태로 어느 자료를 참조했는지 표시.

=== 사용자 자료 ===
${notes}`,
    messages: [{ role: "user", content: question }],
  });
  return res.content[0].text;
}

const question = process.argv.slice(2).join(" ");
ask(question).then(console.log);
```

실행:
```
npm install @anthropic-ai/sdk dotenv
node assistant.js "지난주 결정사항 요약"
```

#### Vector DB 모드 — ChromaDB + Python

(자료 100건 이상이거나 긴 문서일 때)

자료 추출은 동일 (위 가이드 참조).

`requirements.txt`:
```
chromadb
anthropic
openai
python-dotenv
```

`build_index.py` (자료 → 청크 → 임베딩 → ChromaDB 저장):
```python
import os, glob
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()
openai = OpenAI()
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("my_notes")

CHUNK_SIZE = 800  # 글자 기준
files = glob.glob("data/notes/*.md")

docs, ids, metas = [], [], []
for f in files:
    text = open(f, encoding="utf8").read()
    name = os.path.basename(f).replace(".md", "")
    # 800자 단위로 청크 분할
    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i:i+CHUNK_SIZE]
        docs.append(chunk)
        ids.append(f"{name}-{i}")
        metas.append({"source": name, "offset": i})

# 임베딩 생성 (배치)
print(f"[embed] {len(docs)}개 청크 임베딩 시작...")
BATCH = 100
for i in range(0, len(docs), BATCH):
    batch = docs[i:i+BATCH]
    res = openai.embeddings.create(model="text-embedding-3-small", input=batch)
    embeddings = [d.embedding for d in res.data]
    collection.add(
        documents=batch,
        embeddings=embeddings,
        ids=ids[i:i+BATCH],
        metadatas=metas[i:i+BATCH],
    )
    print(f"  ... {i+len(batch)}/{len(docs)}")

print(f"[done] ChromaDB에 {collection.count()}개 청크 저장")
```

`ask.py` (질문 → 검색 → Claude):
```python
import sys, os
from openai import OpenAI
from anthropic import Anthropic
import chromadb
from dotenv import load_dotenv

load_dotenv()
openai = OpenAI()
anthropic = Anthropic()
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_notes")

question = " ".join(sys.argv[1:])

# 1. 질문을 임베딩으로 변환
q_emb = openai.embeddings.create(
    model="text-embedding-3-small", input=[question]
).data[0].embedding

# 2. ChromaDB에서 가장 비슷한 5개 청크 검색
results = collection.query(query_embeddings=[q_emb], n_results=5)
chunks = results["documents"][0]
sources = [m["source"] for m in results["metadatas"][0]]

context = "\n\n---\n\n".join(
    f"[출처: {s}]\n{c}" for c, s in zip(chunks, sources)
)

# 3. Claude에 검색 결과 + 질문 같이 전송
res = anthropic.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1500,
    system=f"""당신은 사용자의 개인 노트 base AI 비서입니다.
아래는 질문과 가장 비슷한 자료 5개입니다. 이 자료에서만 근거를 찾아 답하세요.
근거가 없으면 "확실치 않습니다"라고 답하세요.
답변 마지막에 "(출처: 자료 X, Y)" 표시.

=== 검색된 자료 ===
{context}""",
    messages=[{"role": "user", "content": question}],
)
print(res.content[0].text)
```

실행:
```
pip install -r requirements.txt
python build_index.py    # 1회 (자료 추가될 때마다 재실행)
python ask.py "지난주 결정사항 요약"
```

> "Vector DB 모드는 첫 인덱싱이 5~30분 (자료 양에 따라). 그 후 질문은 1~2초로 빠름. 일반 사용자가 매일 쓰는 형태에는 이쪽이 맞아요."

---

### Turn 6: 첫 질문 테스트

> "이제 본인 비서에게 첫 질문을 던져요. Turn 2에서 적은 5개 질문 중 1번을 그대로 써요."

학습자가 실행:
```
ruby assistant.rb "본인 첫 질문"
# 또는
node assistant.js "본인 첫 질문"
# 또는
python ask.py "본인 첫 질문"
```

> "5~30초 안에 답이 와요. **답이 본인 자료 안의 내용을 정확히 반영하는지** 확인하세요."

3가지 시나리오 분기:

**시나리오 A — 답이 정확하다**
> "축하해요! 본인 비서가 살아 움직여요. 다음 4개 질문도 똑같이 던져 봐요."

**시나리오 B — 답이 부정확하거나 자료에 없는 내용**
> "체크리스트:"
> "1. 자료 폴더에 실제로 그 정보가 들어 있나요? (자료 자체에 없으면 비서도 답 못함)"
> "2. system prompt에 '근거가 없으면 확실치 않다고만 답하라' 들어 있나요?"
> "3. (Vector DB 모드) 검색된 5개 청크에 관련 내용이 있나요? `print(chunks)` 추가해서 확인."

**시나리오 C — 비서가 헛소리(환각)**
> "system prompt를 강화하세요. 다음 문장을 추가:"
```
**중요**: 위 자료에 명시되지 않은 내용은 절대 추측하거나 만들지 마세요.
"자료에서 찾지 못했어요. 더 구체적으로 알려 주시면 다시 찾아볼게요"라고만 답하세요.
```
> "그리고 Anthropic SDK 호출 시 `temperature: 0.3` 추가. 보수적으로 답하게."

> "5개 질문 모두 던지고 결과를 적어 주세요. 정확/부정확 비율을 알려 주세요."

---

### Turn 7: 정확도 검증 + 인터페이스 선택

학습자가 5개 질문 테스트 결과를 보고:
- 5/5 정확 → 다음 단계로
- 3~4/5 정확 → 부정확한 질문 분석 → 자료 보강 또는 system prompt 수정 후 재시도
- 0~2/5 정확 → 자료 자체가 부족하거나 모드가 안 맞음. 같이 진단

> "5개 중 [N개] 정확. [좋아요/조금 더 손볼 부분이 있어요]."

> "비서가 잘 돌아가니까, **언제 어디서 호출할지** 결정해요. 옵션:"

```
A) 터미널에서 매번 호출 (오늘까지 한 방식)
   → 빠르지만 매번 터미널 열어야 함.
   → 본인이 개발자/터미널 익숙한 사람에게 OK.

B) Claude Desktop에서 호출 (Skill로 등록)
   → /my-assistant 같은 명령으로 부르기.
   → 단, 자료가 본인 PC에서 자동 로드되도록 추가 셋업 필요.

C) 본인 SaaS 안에 채팅 UI 추가
   → app/views/assistant/chat.html.erb 같은 페이지 만들기.
   → Turbo Stream으로 답변 스트리밍.
   → 본인만 접근 가능하게 인증 추가.

D) 디스코드/카톡 봇 형태 (6-3 응용)
   → 디스코드 봇이 메시지를 받으면 본인 비서에 질문 전달.
   → 본인이 어디 있든 모바일로 접근 가능.
```

> "본인은 어떻게 호출하고 싶어요?"

학습자 응답에 따라 추가 가이드 (간략히):
- A → 그대로 사용. `alias` 만들어서 `myai "질문"` 같이 짧게.
- B → SKILL.md에 호출 시 자료를 다시 로드하는 절차 명시. v6-plugin 패턴 응용.
- C → Rails 컨트롤러 + 뷰 추가. 코드는 별도 요청 시 생성.
- D → v6-chatbot의 디스코드 봇 코드를 가져와서 응답 부분만 본인 assistant 호출로 교체.

---

### Turn 8: 산출물 저장 + 다음 lesson 안내

> "본인 개인 AI 비서가 살아 움직여요. 본인이 그 동안 쌓은 자료 전체를 기억하는 도우미예요. 매번 본인이 처음부터 컨텍스트 입력할 필요 없어요."

> "오늘 만든 내용을 정리한 파일을 만들어 드려요."

`learn-outputs/ch6-5-ai-assistant.md` 생성:

```markdown
# Ch.6-5 — 내 개인 AI 비서

## 자료 정보
- 위치: [Notion / Obsidian / 폴더 경로 등]
- 카테고리: [독서 노트 / 회의록 / 블로그 / ...]
- 건수: [학습자 자료 건수]
- 평균 길이: [짧음 / 중간 / 김]
- 총 글자수: 약 [N]자

## 선택한 모드
- [✓] 긴 컨텍스트 모드 (자료 < 10만자)
- [ ] Vector DB 모드 (ChromaDB / Pinecone)

## 셋업 정보
- 언어: [Ruby / Node / Python]
- 키 보관: ANTHROPIC_API_KEY (위치: [.env / 1Password])
- (Vector DB 시) OPENAI_API_KEY (위치: [...])

## 자료 변환
- 자료 폴더: data/notes/
- 파일 수: [N]개
- 변환 도구: [Notion export / pandoc / 수동 ...]

## 코드 위치
- 메인 파일: [assistant.rb / assistant.js / ask.py]
- (Vector DB 시) 인덱싱 파일: build_index.py
- (Vector DB 시) DB 위치: ./chroma_db/

## System Prompt 핵심
- "위 자료에서만 근거를 찾아 답한다"
- "근거가 없으면 '확실치 않다'고만 답한다"
- "답변 마지막에 (출처: 자료 X, Y) 표시"

## 5개 검증 질문 결과
| # | 질문 | 답변 요약 | 정확? |
|---|------|----------|-------|
| 1 | ... | ... | ✅/❌ |
| 2 | ... | ... | ✅/❌ |
| 3 | ... | ... | ✅/❌ |
| 4 | ... | ... | ✅/❌ |
| 5 | ... | ... | ✅/❌ |

전체 정확도: [N/5]

## 호출 방법
- [터미널 / Claude Desktop / 본인 SaaS 채팅 UI / 디스코드 봇]
- 명령: [학습자가 정한 호출 방법 — 예: `myai "질문"` alias]

## 다음 단계
- [ ] 자료가 자주 바뀐다면: 매일 새벽 자동 재로드/재인덱싱 (ActiveJob 또는 cron)
- [ ] 정확도가 낮은 질문 패턴을 모아서 자료 보강
- [ ] 모바일에서 쓰고 싶으면 디스코드 봇 형태로 옮기기 (6-3 응용)
- [ ] 자료가 너무 많아지면 긴 컨텍스트 → Vector DB로 마이그레이션
- [ ] 출처 표시(citation)를 클릭 가능한 링크로 — 본인 노트 위치로 점프

## 다음 lesson
- 6-6 Hermes 에이전트 소개 (Vuild 자체 도구) — 마케팅 콘텐츠 자동 생성
```

마무리:
> "본인이 그 동안 쌓은 자료 전체가 살아 있는 비서가 됐어요. 매주 회의 준비, 새 글 아이디어, 의사 결정 회고가 1번 질문으로 끝나요."

> "잠깐 정리:"
> "1. RAG의 핵심을 이해했어요 — '답하기 전에 본인 자료를 먼저 찾는다'."
> "2. 본인 자료 양에 맞춰 모드(긴 컨텍스트 vs Vector DB)를 결정했어요."
> "3. 본인 자료를 추출해서 비서에 주입했어요."
> "4. 5개 질문으로 정확도를 검증했어요."

> "이게 모든 '본인 데이터 기반 AI'의 패턴이에요. 회사 위키 검색, 고객 데이터 Q&A, 본인 코드베이스 검색 — 전부 같은 RAG 패턴."

> "다음 lesson은 6-6 Hermes 소개예요. 이번엔 본인이 직접 만드는 도구가 아니라 Vuild가 본인 SaaS 정보를 외운 마케팅 인턴을 24시간 옆에 두는 형태예요."

> "이어서 진행하려면 학습 사이트의 다음 lesson(6-6)을 열어 주세요."

---

## 막히는 지점 — 미리 답

**① "벡터", "임베딩"이 무서워요**
세부 수학은 몰라도 돼요. 핵심은 한 문장: "텍스트 → 숫자 묶음(좌표) → 비슷한 의미는 좌표가 가까움". 그래서 검색이 키워드가 아닌 "의미"로 가능해요. 예: "주말 매출"과 "토요일 수익"이 의미상 가까워서 같이 잡힘.

**② 답변 정확도가 낮아요**
(1) 청크를 너무 작게 쪼개면 컨텍스트 부족. 500~1000자 추천. (2) 검색 결과 N을 3에서 5~8로 늘려 보세요. (3) "근거가 자료에 없으면 '확실치 않음'이라고만 답하세요" system prompt 추가. (4) 자료 자체에 그 정보가 없으면 비서도 답 못함 — 자료 보강 우선.

**③ Vector DB 운영이 부담돼요**
ChromaDB는 본인 PC/서버에서 SQLite처럼 파일 1개로 동작. 별도 서버 불필요. 자료 1만 건까지 충분. 그 이상이면 Pinecone(클라우드, 월 $0~$70).

**④ 자료 갱신이 자주 일어나요**
긴 컨텍스트 모드: 코드가 매번 폴더 다시 읽으므로 자동 갱신. Vector DB 모드: ActiveJob/cron으로 매일 새벽 `build_index.py` 재실행 (새 자료만 추가하도록 수정 가능). 6-2 자동화 응용.

**⑤ 비서가 출처를 거짓으로 만들어요**
system prompt에 "출처는 정확히 검색된 자료명만 인용. 만들지 말 것" 명시 + Vector DB 모드라면 검색된 자료명을 코드 단에서 강제 표시(LLM이 만들 여지 안 줌).

**⑥ Notion 자료 export가 너무 많아서 정리가 어려워요**
2단계로 가요. (1) 일단 가장 중요한 카테고리(예: 올해 회의록, 최근 블로그) 50건만 export → 긴 컨텍스트 모드로 빠르게 동작 확인. (2) 흐름 익숙해진 후 전체 자료 → Vector DB로 마이그레이션.

**⑦ 응답이 너무 길거나 토큰 비용이 부담돼요**
`max_tokens`를 1500에서 800으로 줄임. system prompt에 "3문단 이내로 답하라" 명시. 또는 Sonnet 대신 Haiku 모델 사용 (1/5 비용, 한국어도 충분).

**⑧ 본인 SaaS 안에 비서를 넣고 싶어요**
긴 컨텍스트 모드면 그대로 Rails 컨트롤러 안에서 호출하면 됨. Vector DB 모드면 ChromaDB는 같은 서버에 두고, Pinecone이면 API로 호출. 인증 필수 — 본인만 접근 가능하게 `before_action :authenticate`.
