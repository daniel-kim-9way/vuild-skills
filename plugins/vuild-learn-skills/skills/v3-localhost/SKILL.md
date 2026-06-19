---
name: v3-localhost
description: "bin/dev 또는 npm run dev로 본인 PC에 서버를 띄우고 localhost:3000을 브라우저로 열어 본인 서비스를 처음 보는 모먼트. Live reload 체험 + 자주 막히는 지점 해결. Triggers: \"v3 localhost\", \"v3-localhost\", \"localhost\", \"bin dev\", \"서버 띄우기\", \"로컬 서버\""
---

# V3: localhost 띄우기 + 화면 확인

## 학습 목표
- `bin/dev`(Rails) 또는 `npm run dev`(Node) 명령으로 본인 PC에 개발 서버를 띄운다
- 브라우저에서 `http://localhost:3000`을 열어 본인 서비스를 본인 눈으로 확인한다
- 코드를 한 줄 수정 → 저장 → 브라우저가 자동 새로고침되는(live reload) 사이클을 몸에 익힌다
- 포트 충돌 / 의존성 누락 / 무한 로딩 등 첫날 가장 자주 만나는 문제를 본인 손으로 해결한다

## 사전 조건
- Ch.4-5(빌드킷 `/setup`) 완료 — `.env` 파일이 있고 `bundle install`이 끝나 있음
- Antigravity가 본인 PC에 깔려 있고 본인 빌드킷 폴더가 열려 있음
- 사용 중인 브라우저(Chrome / Edge / Safari) 1개

## 대화형 학습 프로토콜

이 스킬은 대화형 코칭 방식을 따릅니다. 강의가 아닌 질문-답변-피드백 루프로 진행합니다.

### 진행 방식
1. references/main.md를 읽고 대화 흐름(Turn 1 ~ Turn 7)에 따라 진행
2. 각 Turn에서 학생이 본인 PC에서 실제로 명령을 실행하고, 출력 결과를 보고하면 그 출력을 함께 해석
3. 에러가 나면 에러 메시지를 한 줄씩 풀어 주고 해결책 제시
4. 마지막 Turn에서 본인 localhost URL + 캡쳐 메모 + 첫 live reload 경험을 파일로 저장

### 산출물
- 파일명: `learn-outputs/ch4-9-localhost.md`
- 내용: 본인 localhost URL + 부팅 로그 마지막 줄 + 첫 live reload로 바꾼 한 줄 + 만났던 에러(있으면) + 해결 방법 메모
