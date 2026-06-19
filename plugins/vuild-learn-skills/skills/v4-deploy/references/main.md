## EXPLAIN

### localhost의 한계

지금까지 만든 서비스는 `http://localhost:3000`에서 돌아갑니다.

이 주소의 의미는 **"내 컴퓨터 안에만 있다"**입니다.

친구에게 이 링크를 카카오톡으로 보내도 볼 수 없습니다. 부모님에게 보여드릴 수도 없습니다. 투자자에게 "제 서비스 한번 보세요"라고 할 수도 없습니다.

마치 **집 안 TV**와 같습니다. 아무리 좋은 프로그램을 틀어도 집 밖에서는 볼 수 없습니다.

### 배포란?

**배포(Deploy)**는 서비스를 인터넷 어딘가의 컴퓨터(서버)에 올려서, 전 세계 누구든 접근할 수 있게 만드는 작업입니다.

배포 후에는:
- `https://내서비스.railway.app` 같은 **공개 URL**이 생깁니다
- 내 컴퓨터를 꺼도 **24시간** 돌아갑니다
- **전 세계** 어디서든 접근할 수 있습니다
- 카카오톡, 인스타그램에 **링크를 공유**할 수 있습니다
- 휴대폰으로도 접속할 수 있습니다

> **이 URL을 누구에게든 보내면 볼 수 있습니다.**

이것이 오늘의 순간입니다.

### PaaS: 원클릭 배포의 시대

옛날에는 배포가 정말 어려웠습니다. 서버 컴퓨터를 사고, 운영체제를 설치하고, 네트워크를 설정하고... 전문 시스템 관리자가 필요했습니다.

지금은 다릅니다. **PaaS(Platform as a Service)**라는 서비스가 있습니다.

PaaS는 **코인 빨래방**과 같습니다:
- 세탁기를 살 필요 없이, 빨래를 넣고 버튼만 누르면 됩니다
- 세탁기 고장? 가게에서 알아서 고칩니다
- 사용한 만큼만 돈을 냅니다

마찬가지로 PaaS에서는:
- 서버를 살 필요 없이, 코드를 올리고 버튼만 누릅니다
- 서버 문제? PaaS가 알아서 처리합니다
- 사용한 만큼만 과금됩니다

### Railway vs Render

두 서비스 모두 좋습니다. Rails 앱에는 **Railway**를 추천합니다.

| | Railway | Render |
|--|---------|--------|
| **난이도** | 매우 쉬움 | 쉬움 |
| **무료 플랜** | $5 크레딧/월 | 750시간/월 (활동 시) |
| **배포 속도** | 빠름 (2~3분) | 보통 (5~10분, 무료는 더 느림) |
| **GitHub 연동** | 자동 배포 (push하면 자동 반영) | 자동 배포 |
| **Rails 지원** | 매우 좋음 (자동 감지) | 좋음 |
| **데이터베이스** | 원클릭 PostgreSQL | 원클릭 PostgreSQL |
| **수면 모드** | 무료 플랜에서 비활성 시 대기 | 무료 플랜에서 15분 비활성 시 수면 |

**Railway 추천 이유**: GitHub 리포지토리를 연결하면 Rails 앱을 자동으로 감지하고, 거의 설정 없이 배포해줍니다. `git push`만 하면 자동으로 최신 버전이 반영됩니다.

> **참고**: Kamal을 이용한 직접 서버 배포는 C7(Advanced) 과정에서 다룹니다. 지금은 PaaS로 빠르게 배포하는 것에 집중합니다.

### Production 환경: 개발과 다른 세계

지금까지는 **개발 환경(development)**에서 작업했습니다. 배포하면 **프로덕션 환경(production)**으로 바뀝니다.

| | 개발 환경 (localhost) | Production (배포 후) |
|--|----------|------------|
| **목적** | 빠른 수정, 디버깅 | 안정적 운영 |
| **오류 표시** | 상세 정보 (코드 위치까지) | 간단한 메시지만 (보안) |
| **성능** | 최적화 안 됨 | 캐싱, 압축 적용 |
| **비밀 키** | .env 파일 | 서버의 환경 변수 |
| **데이터베이스** | SQLite (로컬) | PostgreSQL (서버) |
| **접근** | 나만 | 전 세계 누구나 |

가장 큰 차이는 **오류 표시**입니다. 개발 환경에서는 오류가 나면 "어디에서 왜 오류가 났는지" 상세하게 보여줍니다. 하지만 Production에서 이걸 보여주면 공격자에게 시스템 구조를 알려주는 것과 같습니다. 그래서 Production에서는 "문제가 발생했습니다" 같은 간단한 메시지만 보여줍니다.

### git push → 자동 배포의 마법

Railway를 설정하면 이런 마법이 일어납니다:

```
[내 컴퓨터]                        [Railway 서버]
코드 수정                          
   ↓
git add + git commit
   ↓
git push                    →    "새 코드 감지!"
                                    ↓
                                 자동 빌드 시작
                                    ↓
                                 테스트 실행
                                    ↓
                                 배포 완료!
                                    ↓
                                 새 버전 라이브! ✨
```

코드를 수정하고 `git push`만 하면 **자동으로** 최신 버전이 배포됩니다. 별도로 서버에 접속하거나 파일을 업로드할 필요가 없습니다.

이것이 현대 배포의 기본입니다.

## EXECUTE

### 단계 0: Vuild 출시 정보 등록 (배포 전 5분)

배포 URL이 생기기 전에 먼저 **Vuild 대시보드**에 출시 정보를 등록합니다.

> "Vuild 대시보드 → 해당 프로젝트 → 'LAUNCH' 또는 'checklist' 탭으로 이동하세요."

입력할 5가지 정보:

| # | 항목 | 예시 |
|---|------|------|
| 1 | **서비스 이름** | 북메모리 |
| 2 | **한 줄 설명** | 책을 읽고 핵심만 기억하는 AI 독서 노트 |
| 3 | **타겟 사용자** | 독서를 좋아하지만 기억력이 걱정인 직장인 |
| 4 | **서비스 URL** | (배포 후 채울 것 — 일단 빈칸) |
| 5 | **연락처 이메일** | 운영자 이메일 |

> "이 정보는 나중에 Showcase 등록과 첫 사용자 공유 메시지에 그대로 쓰여요. 지금 5분 투자하면 나중에 편합니다."

입력 완료 후 다음 단계로.

---

### 단계 1: Production 환경 준비

배포 전에 서비스를 production 환경에 맞게 준비합니다.

Claude Code에서:
```
서비스를 Railway에 배포하려고 해.
production 환경 준비를 해줘.

필요한 것:
- Procfile 설정 (web: bin/rails server -p $PORT -e production)
- database.yml에 production 설정 (PostgreSQL)
- Gemfile에 pg gem 추가 (production 그룹)
- config/environments/production.rb 확인
  - HTTPS 강제 (config.force_ssl = true)
  - 정적 파일 서빙 (config.public_file_server.enabled = true)
- SECRET_KEY_BASE 환경 변수 처리
- 환경 변수 목록 정리 (어떤 변수들을 Railway에 설정해야 하는지)
```

> **에러가 나면**: production 준비 중 가장 흔한 문제는 `pg` gem 설치 에러입니다. 로컬에서 PostgreSQL이 없어도 괜찮습니다. `gem 'pg'`를 Gemfile의 `group :production`에만 넣으면 로컬에서는 설치하지 않습니다.

### 단계 2: GitHub에 코드 올리기

Railway는 GitHub에서 코드를 가져옵니다. 먼저 최신 코드를 GitHub에 올립니다.

```bash
git add .
git commit -m "production 배포 준비"
git push origin main
```

> **GitHub 리포지토리가 없다면**: C3에서 만들었을 수 있습니다. 없다면 GitHub에서 새 리포지토리를 만들고 연결하세요. Claude에게 "GitHub 리포지토리 만들고 연결해줘"라고 하면 안내해줍니다.

### 단계 3: Railway 계정 만들기 + 프로젝트 생성

1. https://railway.app 접속
2. "Login" → **GitHub 계정으로 로그인** (추천)
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택
5. 내 서비스 리포지토리 선택
6. Railway가 자동으로 Rails 앱을 감지합니다

### 단계 4: 데이터베이스 추가

1. 프로젝트 화면에서 "New" → "Database" → "PostgreSQL" 선택
2. PostgreSQL이 자동으로 프로비저닝됩니다
3. Railway가 `DATABASE_URL` 환경 변수를 자동으로 설정합니다

### 단계 5: 환경 변수 설정

프로젝트 → 서비스 클릭 → "Variables" 탭:

필수 환경 변수:
```
RAILS_ENV=production
RAILS_MASTER_KEY=[config/master.key 파일의 값]
SECRET_KEY_BASE=[Rails에서 생성한 값]
```

선택 환경 변수 (해당되는 것만):
```
ANTHROPIC_API_KEY=[AI 기능을 넣었다면]
TOSS_CLIENT_KEY=[결제 기능을 넣었다면]
TOSS_SECRET_KEY=[결제 기능을 넣었다면]
```

> **RAILS_MASTER_KEY는 어디에?**: 프로젝트 폴더의 `config/master.key` 파일을 열면 있습니다. 이 파일은 .gitignore에 포함되어 GitHub에 올라가지 않으므로, 직접 복사해서 Railway에 넣어야 합니다.

### 단계 6: 배포 시작!

환경 변수를 설정하면 Railway가 **자동으로 빌드를 시작**합니다.

빌드 로그를 지켜봅니다:
1. "Deployments" 탭 클릭
2. 최신 배포의 로그 확인
3. "Building..." → "Deploying..." → **"✅ Deployed!"**

빌드가 보통 2~5분 걸립니다.

**배포 실패 시 대응:**

가장 흔한 오류 3가지:

**1. "bundle install failed"**
```
Railway 배포 중 bundle install이 실패했어.
오류: [오류 메시지]
해결해줘.
```
원인: 보통 `pg` gem이나 다른 네이티브 gem의 빌드 문제입니다.

**2. "Asset precompilation failed"**
```
Railway 배포 중 asset precompile이 실패했어.
오류: [오류 메시지]
해결해줘.
```
원인: JavaScript나 CSS 관련 설정 문제입니다.

**3. "Application Error" (배포 후)**
```
Railway에 배포는 됐는데 서비스에 접속하면 "Application Error"가 나와.
Railway 로그에 이 오류가 있어:
[오류 메시지]
해결해줘.
```
원인: 환경 변수 누락, 데이터베이스 마이그레이션 미실행 등

> **꿀팁**: 배포 실패는 **정상적인 과정**입니다. 프로 개발자도 첫 배포에서 2~3번은 실패합니다. 오류 메시지를 Claude에게 보내면 대부분 해결됩니다. 포기하지 마세요!

### 단계 7: 데이터베이스 마이그레이션

배포 후 데이터베이스 테이블을 생성해야 합니다.

Railway에서:
1. 서비스 클릭 → "Settings" 탭
2. "Custom Start Command" 또는 Procfile에서 release 명령 설정

또는 Claude에게:
```
Railway에서 데이터베이스 마이그레이션을 실행하는 방법을 알려줘.
Procfile에 release 단계를 추가해줘.
```

### 단계 8: THE MOMENT

배포가 완료되면 Railway가 URL을 알려줍니다.

`https://내서비스이름.up.railway.app`

---

**잠시 멈추세요.**

이 URL을 클릭하기 전에, 한 발 물러서서 이 순간을 느껴보세요.

몇 주 전에 "코딩을 모르는 나"였습니다.
C1에서 아이디어를 떠올렸습니다.
C2에서 기획서를 만들었습니다.
C3에서 코드를 작성했습니다.
C4에서 디자인하고, 보안을 점검했습니다.

그리고 지금...

---

**브라우저에서 그 URL을 열어봅니다.**

내가 만든 서비스가 인터넷에 있습니다.

**이 URL을 복사해서 카카오톡으로 보내봅니다.**

아무에게나 — 가족, 친구, 동료.

"나 이거 만들었어."

상대방이 클릭하면 **볼 수 있습니다.** 진짜로.

---

**이제 휴대폰을 꺼내세요.**

폰의 브라우저에서 그 URL을 입력합니다.

주머니 속 폰에서 내가 만든 서비스가 열리는 순간.

이것이 **THE MOMENT**입니다.

---

### 단계 9: 도메인 연결 (선택)

Railway 기본 URL(`xxx.up.railway.app`)도 충분하지만, 내 도메인을 연결하면 더 전문적으로 보입니다.

**도메인 구매:**
- 가비아 (gabia.com) — 한국 최대 도메인 업체
- AWS Route 53 — 안정적이고 글로벌
- 가격: .com 연간 약 15,000원, .kr 연간 약 18,000원

**Railway에서 도메인 연결:**
1. 프로젝트 → 서비스 → "Settings"
2. "Custom Domain" → 내 도메인 입력 (예: myservice.kr)
3. Railway가 안내하는 DNS 설정을 도메인 업체에서 적용
4. CNAME 레코드 추가
5. 5~30분 후 내 도메인으로 접속 확인

도메인 연결은 지금 안 해도 됩니다. 서비스가 자리잡고 나서 해도 늦지 않습니다.

### 단계 10: 배포 후 확인

배포가 완료되면 마지막 점검을 합니다:

```
배포된 서비스의 최종 점검을 해줘:
- 메인 페이지가 정상적으로 로드되는지
- 로그인/가입이 되는지
- 핵심 기능이 동작하는지
- 모바일에서도 접속되는지
- HTTPS가 적용되었는지 (URL이 https://로 시작하는지)
```

> **막혔을 때**: 배포 후 가장 흔한 문제는 "로컬에서는 되는데 서버에서는 안 되는" 경우입니다. 대부분 환경 변수 누락이나 데이터베이스 관련 문제입니다. Railway의 로그를 확인하고 Claude에게 보여주면 해결됩니다.

## QUIZ

AskUserQuestion({
  "questions": [
    {
      "question": "localhost:3000이 다른 사람에게 보이지 않는 이유는?",
      "header": "배포 개념",
      "options": [
        {"label": "서비스에 버그가 있어서", "description": ""},
        {"label": "서비스가 내 컴퓨터에만 존재하고 인터넷에 공개되지 않아서", "description": ""},
        {"label": "비밀번호가 설정되어 있어서", "description": ""},
        {"label": "포트 번호가 잘못돼서", "description": ""}
      ],
      "multiSelect": false
    },
    {
      "question": "Railway에서 코드를 수정한 후 배포하려면?",
      "header": "자동 배포",
      "options": [
        {"label": "Railway 서버에 직접 접속해서 파일을 교체한다", "description": ""},
        {"label": "git push만 하면 자동으로 배포된다", "description": ""},
        {"label": "Railway에 이메일을 보내서 요청한다", "description": ""},
        {"label": "매번 새 프로젝트를 만든다", "description": ""}
      ],
      "multiSelect": false
    },
    {
      "question": "배포 실패 시 가장 먼저 할 일은?",
      "header": "트러블슈팅",
      "options": [
        {"label": "다른 PaaS로 옮긴다", "description": ""},
        {"label": "처음부터 다시 만든다", "description": ""},
        {"label": "배포 로그의 오류 메시지를 확인하고 Claude에게 보여준다", "description": ""},
        {"label": "포기한다", "description": ""}
      ],
      "multiSelect": false
    }
  ]
})

정답:
- 1번 → "서비스가 내 컴퓨터에만 존재하고 인터넷에 공개되지 않아서"
- 2번 → "git push만 하면 자동으로 배포된다"
- 3번 → "배포 로그의 오류 메시지를 확인하고 Claude에게 보여준다"

해설:
- localhost: "내 컴퓨터"를 가리키는 주소입니다. 배포는 코드를 인터넷 서버로 옮겨서 공개 URL을 만드는 작업입니다.
- 자동 배포: Railway와 GitHub을 연결하면 git push할 때마다 자동으로 최신 버전이 배포됩니다. 이것이 현대 배포의 기본입니다.
- 트러블슈팅: 배포 실패는 프로 개발자도 겪는 정상적인 과정입니다. 로그의 오류 메시지가 해결의 열쇠입니다. Claude에게 보여주면 대부분 해결됩니다.
