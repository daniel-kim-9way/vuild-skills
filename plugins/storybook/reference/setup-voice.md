# 목소리 준비

## 기본 목소리 (edge-tts)

설치할 것도 키도 없어요. 마이크로소프트 신경망 목소리 셋 중에 골라요.

| ID | 이름 |
|---|---|
| ko-KR-SunHiNeural | 선희 (여) |
| ko-KR-InJoonNeural | 인준 (남) |
| ko-KR-HyunsuMultilingualNeural | 현수 (남) |

`sb voice-samples`를 하면 세 목소리가 같은 문장을 읽는 화면이 열려요. 들어 보고 고르면 돼요.

## Fish Audio

무료 모델(s2.1-pro-free)로 읽어요. 남이 만든 목소리를 고르거나, 내 목소리를 녹음해서 복제할 수 있어요.

1. fish.audio에 가입해요.
2. API 키 화면(fish.audio/app/api-keys)에서 키를 만들고 복사해요.
3. 목소리 ID를 구해요.
   - 남의 목소리: 목소리 모음에서 한국어 목소리를 골라요. 그 목소리 페이지 주소 끝의 긴 영문·숫자가 ID예요.
   - 내 목소리: 녹음 파일을 올려 새 목소리를 만들고, **공개 범위를 비공개(Private)로** 해요. 내 목소리 화면(fish.audio/app/my-voices)에서 그 목소리를 열면 주소 끝이 ID예요.
4. `sb env open` → `FISH_AUDIO_API_KEY=`와 `FISH_VOICE_ID=`를 채우고 저장해요.
5. `sb settings voice fish` → `sb fish check`
   - 내 목소리인데 «공개»로 나오면 Fish Audio에서 비공개로 바꾸고 다시 확인해요. 내 목소리가 공개돼 있으면 누구나 그 목소리로 말을 만들 수 있어요.

- Fish Audio가 안 되는 날은 기본 목소리(선희)로 읽어요. 한 동화 안에서 목소리가 섞이지 않게 앞쪽도 선희로 다시 읽어요.
