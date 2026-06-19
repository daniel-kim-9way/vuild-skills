## EXPLAIN

### localhost가 뭐예요?

**localhost**는 본인 컴퓨터 자신을 가리키는 주소예요. 인터넷 어딘가의 서버가 아니라, 본인 PC 안에서 도는 작은 서버에, 본인 브라우저로만 접속하는 셈이에요.

비유하면 **집 안에서 켠 라디오**예요. 라디오 송출 안테나는 집 안에만 있어서, 옆집 사람도 못 듣고 친구도 못 듣고, 같은 집에 있는 본인 귀에만 들려요. 인터넷에 올린 게 아니라 **"개발 중인 본인만 보이는 미리보기"**예요.

주소 형식은 이렇게 생겼어요.

```
http://localhost:3000
```

세 부분이 합쳐진 거예요.

- **http**: 브라우저가 서버와 대화하는 약속(규약)
- **localhost**: "본인 PC 자신" (= IP `127.0.0.1`과 같은 뜻)
- **:3000**: 포트 번호 — 본인 PC 안에서 어느 문으로 들어갈지. Rails의 기본 포트.

### 왜 이게 필요해요? 인터넷에 바로 올리면 안 돼요?

올릴 수는 있어요. 그런데 인터넷에 올리는 데는 시간(빌드 + 배포 5분)과 비용이 들어요. 본인이 한 줄 수정할 때마다 5분씩 기다리면 미쳐요.

그래서 개발자들은 항상 **본인 PC에서 먼저 띄워 보고, 다 됐다 싶을 때 인터넷에 올려요.** localhost는 ‘리허설 무대’라고 생각하세요. 본 무대(인터넷)에 올라가기 전에 무한히 연습하는 곳.

### 두 가지 명령

본인 빌드킷이 Rails 기반이면 → `bin/dev`
Node 기반(Next.js 등)이면 → `npm run dev`

빌드킷 종류는 본인 빌드킷 폴더 최상단에 `Gemfile`이 있으면 Rails, `package.json`만 있으면 Node예요. 본 코스는 Rails가 기본.

`bin/dev`는 사실 세 개를 한꺼번에 켜는 ‘지휘자’예요.

```
web — Rails 서버 (Puma)
css — Tailwind CSS 자동 빌드
js  — JavaScript 자동 빌드
```

이 셋이 다 떠 있어야 화면이 제대로 보여요. 그래서 명령 하나로 묶어 둔 거예요.

---

## EXECUTE

### Turn 1: 본인 빌드킷 폴더에 들어와 있나요?

> "지금 Antigravity의 하단 터미널을 한 번 봐 주세요. 터미널 첫 줄에 본인 빌드킷 폴더 경로가 보이나요? 예를 들어 `~/projects/my-cafe-app` 같은."

학생이 답하면 확인:

> "터미널 프롬프트 앞에 본인 빌드킷 폴더 이름이 보이면 OK예요. 보이지 않거나 다른 폴더에 있으면 다음 명령으로 들어가세요:"

```bash
cd ~/projects/[본인 빌드킷 폴더 이름]
```

> "확실하지 않으면 `pwd`(Mac/Linux) 또는 `cd`(Windows)로 현재 위치 확인. `ls`(Mac/Linux) 또는 `dir`(Windows)로 그 폴더 안에 `Gemfile`이나 `package.json`이 보이면 정확히 들어와 있는 거예요."

학생이 OK라고 하면 → Turn 2.

학생이 "폴더가 어디 있는지 모르겠어요"라고 하면:
> "Ch.4-2(빌드킷 압축 풀기)에서 압축 푼 위치를 떠올려 보세요. 보통 `~/projects/` 또는 바탕화면이에요. 못 찾으면 Antigravity 좌측 ‘Open Folder’ 버튼으로 본인 빌드킷 폴더 다시 열기."

---

### Turn 2: 명령어 입력

> "본인 빌드킷이 Rails 기반인지 확인해 봅시다. 터미널에 다음을 입력:"

```bash
ls Gemfile 2>/dev/null && echo "Rails!" || echo "Node?"
```

> "‘Rails!’가 나오면 Rails. ‘Node?’가 나오면 Node 기반이에요."

**Rails 기반인 경우:**

> "이제 서버를 띄워요. 다음 한 줄:"

```bash
bin/dev
```

> "엔터 누르면 화면에 글자가 줄줄 떠요. 보통 5~15초 걸려요. 천천히 기다리세요."

**Node 기반인 경우:**

> "다음 한 줄:"

```bash
npm run dev
```

> "비슷하게 글자가 줄줄 떠요."

> "출력 마지막 부분에 `Listening on ...` 또는 `Local: http://localhost:3000` 같은 줄이 보이면 성공이에요. 출력 화면을 그대로 한 번 복사해서 보여 주세요."

학생이 출력을 보여 주면 → Turn 3.

---

### Turn 3: 출력 메시지 해석

학생이 보내 준 출력을 한 줄씩 풀어 줘요.

**성공 출력 예시(Rails):**

```
11:23:45 web.1     | started with pid 12345
11:23:45 css.1     | started with pid 12346
11:23:45 js.1      | started with pid 12347
11:23:46 web.1     | => Booting Puma
11:23:46 web.1     | => Rails 8.1.x application starting in development
11:23:46 web.1     | * Listening on http://localhost:3000
```

> "각 줄 의미:"

```
11:23:45         — 시각 (지금 시각)
web.1            — 웹 서버(Puma)가 시작됨
css.1, js.1      — Tailwind / JS 빌드도 같이 시작됨
=> Booting Puma  — Rails 서버 부팅 시작
=> Rails ...     — 어떤 환경(development)으로 떴는지
* Listening on   — 가장 중요. 이 주소로 접속 가능
```

> "마지막 줄 `Listening on http://localhost:3000`이 떴으면 서버가 준비된 거예요."

> "**중요**: 이 터미널 창은 닫지 마세요. 닫는 순간 서버도 같이 꺼져요. 다음 단계는 **새 브라우저 창**으로 이동."

만약 학생 출력에 `Listening on` 줄이 없거나 빨간색 에러가 있으면 → "에러 처리" 섹션(Turn 6)으로 점프.

---

### Turn 4: 브라우저 열고 localhost:3000 접속

> "브라우저(Chrome 권장)를 열고 새 탭에서 주소창에 다음 입력:"

```
http://localhost:3000
```

> "엔터. 잠깐(2~5초) 기다려요."

**무엇이 떠야 정상인가:**

본인 빌드킷의 메인 페이지가 떠야 해요. Ch.4-6에서 만든 회원가입·로그인 화면, 또는 Ch.4-8의 OAuth 페이지일 수도 있어요. 본인 서비스의 첫 화면이 뭔지는 빌드킷에 따라 달라요.

> "화면이 떴으면 한 번 캡쳐해 두세요(`Cmd + Shift + 4` Mac / `Win + Shift + S` Windows). 본인이 만든 첫 서비스 화면이에요. 기록할 가치가 있어요."

> "혹시 다음 메시지가 뜨면 — 어떤 메시지였나요?"

```
A. "이 페이지에 도달할 수 없습니다" / "ERR_CONNECTION_REFUSED"
   → 서버가 안 떴어요. 터미널로 돌아가서 출력 확인. (Turn 6)

B. 빨간 에러 페이지(Rails 에러)
   → 코드 안에 문제가 있어요. 페이지 상단 빨간 글자 한 줄을 그대로
     Claude Code에 붙이고 "이 에러 풀어 줘".

C. 무한 로딩 (스피너만 돌고 안 뜸)
   → 1~2분 기다리세요. asset 빌드가 처음에는 느려요. 그 이상이면 Turn 6.

D. 본인 서비스 화면 정상
   → 축하해요. Turn 5로.
```

---

### Turn 5: Live Reload 체험

> "지금부터 마법을 봐요. 코드 한 줄을 수정해서, 브라우저가 자동으로 새로고침되는 걸 보는 거예요."

> "Antigravity 좌측 파일 트리에서 다음 파일 중 아무거나 하나 열어 주세요. 보통 메인 페이지의 텍스트가 들어 있는 파일이에요."

```
Rails 빌드킷의 경우:
- app/views/home/index.html.erb
- app/views/pages/home.html.erb
- app/views/landing/index.html.erb
(빌드킷에 따라 다름. 본인 빌드킷에 어떤 파일이 있나 보세요.)
```

> "파일을 못 찾겠으면 Claude Code에 ‘본인 빌드킷의 메인 페이지 view 파일 경로 알려 줘’ 한 줄."

> "파일을 열었으면, 화면에 보이는 텍스트(예: 제목 ‘안녕하세요’) 한 줄을 찾아서 살짝 바꿔요. 예: ‘안녕하세요’ → ‘안녕하세요 ✨’"

> "그리고 저장(`Cmd + S` Mac / `Ctrl + S` Windows)."

> "저장한 즉시(또는 1~2초 후) 브라우저로 돌아가 보세요. 새로고침 안 눌러도 자동으로 변경 반영돼요. 본인 눈으로 확인."

> "안 바뀌어 있으면? 본인이 직접 새로고침(`F5` 또는 `Cmd + R`). 그래도 안 바뀌면 다음을 시도:"

```
1. 파일이 진짜 저장됐는지 확인 (제목 옆에 ● 표시 사라졌나)
2. 강제 새로고침 (Cmd/Ctrl + Shift + R) — 브라우저 캐시 무시
3. 터미널의 bin/dev 출력 확인 — 빨간 에러가 있나
```

> "이게 개발의 일상 사이클이에요. **코드 수정 → 저장 → 브라우저 확인 → 다시.** 1초 단위로 반복돼요."

---

### Turn 6: 자주 발생하는 문제 해결

학생이 어디서 막혔는지 듣고 해당 항목으로 안내. 이 Turn은 학생이 막혔을 때만 들어와요.

#### A. "포트 3000이 이미 사용 중입니다 / Address already in use"

> "이전 서버가 안 꺼지고 남아 있을 가능성이 가장 높아요. 다음 한 줄로 잡아 죽여요:"

```bash
# Mac / Linux
lsof -ti:3000 | xargs kill -9

# Windows (PowerShell)
netstat -ano | findstr :3000
# 출력의 마지막 숫자(PID) 확인 후
taskkill /PID 1234 /F
```

> "또는 다른 포트로 시도:"

```bash
bin/rails server -p 4000
# → http://localhost:4000 으로 접속
```

#### B. "서버 시작 안 됨 / 빨간 에러 잔뜩"

> "에러 메시지 첫 5~10줄을 그대로 Claude Code 채팅에 복붙. ‘이 에러 풀어 줘’ 한 줄. 흔한 원인:"

```
- 의존성 누락: bundle install 또는 npm install 다시
- DB 마이그레이션 안 됨: bin/rails db:migrate 한 줄
- .env 파일 없음: cp .env.example .env 한 줄
- Ruby/Node 버전 안 맞음: mise install 또는 nvm use
```

#### C. "브라우저에서 무한 로딩"

> "터미널의 `bin/dev` 출력을 봐요. 보통 거기에 빨간 에러가 떠요. asset compile이 처음에 느린 거면 1~2분 기다리세요. 그 이상이면 Ctrl+C → 다시 `bin/dev`."

#### D. "코드 수정해도 브라우저에 반영 안 됨"

```
1. 저장 확인 (Cmd/Ctrl + S 다시)
2. 강제 새로고침 (Cmd/Ctrl + Shift + R)
3. 서버 재시작 (Ctrl+C → bin/dev 다시)
4. config/environments/development.rb 에서
   config.cache_classes = false 인지 확인 (true면 코드 변경 안 잡힘)
```

#### E. "같은 Wi-Fi 본인 폰으로 접속하고 싶어요"

> "본인 PC IP 확인:"

```bash
# Mac: 시스템 설정 → Wi-Fi → 세부 정보 → IP 주소
# Win: cmd 에서 ipconfig
```

> "그 IP(예: `192.168.0.42`)를 적어 두고 서버를 다음 옵션으로 띄워요:"

```bash
bin/rails server -b 0.0.0.0
```

> "본인 폰 브라우저에서 `http://192.168.0.42:3000` 접속. 같은 Wi-Fi에 접속되어 있어야 해요. 보안상 개발 중에만 사용."

#### F. "서버 끄는 법"

> "`bin/dev`가 도는 터미널 창 클릭 → `Ctrl + C` (Mac도 Cmd 아니라 Ctrl). ‘Goodbye!’ 또는 비슷한 메시지 후 프롬프트가 돌아옴. 다시 시작하려면 그 터미널에서 `bin/dev` 한 번 더."

---

### Turn 7: 산출물 저장

> "본인이 한 일을 한 페이지로 기록해 둬요. 다음 학습에 도움이 됩니다."

본인이 학생의 답변을 모아 `learn-outputs/ch4-9-localhost.md` 파일을 **실제로 생성**한다. 형식:

```markdown
# Ch.4-9 — 본인 PC에서 localhost 띄우기

## 환경
- 빌드킷 종류: [Rails / Node]
- 사용한 명령어: [bin/dev / npm run dev]
- 부팅 시간: 약 [학생이 답한 초]

## 부팅 로그 마지막 줄
```
[학생이 본 Listening on ... 줄 그대로]
```

## 첫 live reload로 바꾼 것
- 파일 경로: [예: app/views/home/index.html.erb]
- 바꾼 내용: [예: "안녕하세요" → "안녕하세요 ✨"]
- 자동 반영됐나: [네 / 새로고침 필요]

## 만났던 에러 (있으면)
- 에러 메시지 한 줄: [복붙]
- 해결 방법: [본인이 어떻게 풀었나]

## 다음에 본인이 기억해야 할 것
- 서버 켜기: bin/dev
- 서버 끄기: Ctrl + C
- 접속 주소: http://localhost:3000
- 자동 반영 안 될 때: Cmd/Ctrl + Shift + R
```

저장 후:

> "축하해요. 본인 PC에서 본인이 만든 서비스가 도는 모먼트를 본 거예요. 이 화면을 매일 볼 거예요. 익숙해지세요."

> "다음 레슨은 4-10 디자인 시스템 적용. 기능은 동작하는데 화면이 좀 못생겼죠? 다음에서 PLAN의 디자인 토큰을 본격적으로 입혀요."

> "다음 스킬: `/v4-design`"
