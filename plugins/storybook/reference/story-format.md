# story.json 모양

동화 하나는 `~/동화공방/동화/<날짜>-<제목>/` 폴더예요. 이 폴더의 `story.json`이 기준이고, HTML·MP4는 다 여기서 다시 만들 수 있어요.

```
story.json   사진/child.jpg toy1.jpg   그림/cover.jpg p1.jpg … p8.jpg   목소리/p0-0.mp3 …
1-글확인.html  2-그림확인.html  동화.html  <제목>.mp4
```

```json
{
  "version": 1, "title": "…", "lesson": "…", "theme": "courage", "wish": "", "music": "lullaby",
  "created": "2026-10-16", "seed": 1234567, "voice_by": "edge:ko-KR-SunHiNeural",
  "cast": [{ "key": "child", "name": "서준", "age": 4, "kind_ko": "아이", "look_en": "…", "photo": "사진/child.jpg" }],
  "questions": ["…", "…"],
  "pages": [
    { "n": 0, "text": "제목", "cast": ["child", "toy1"], "prompt_en": "…", "image": "그림/cover.jpg",
      "redraw_note": "", "voices": ["목소리/p0-0.mp3"], "zones": ["top"] }
  ]
}
```

- `n` 0이 표지, 1~8이 본문이에요.
- `image`가 `null`이거나 그림 파일이 없는 쪽은 아직 안 그린 쪽이에요. `sb draw`는 이런 쪽만 그려요.
- `voice_by`는 어떤 목소리로 읽었는지예요. 목소리 설정이 바뀌면 `sb voice`가 처음부터 다시 읽어요.
- 그리는 동안 폴더에 `.drawing` 표시가 생기고, 다 그리면 지워요.
- `voices`·`zones`는 문장 조각마다 하나씩이에요(표지는 한 덩어리).
- `redraw_note`는 다시 그린 까닭이에요. 그림 확인 화면에 보여요.

## 고치는 법

story.json을 직접 고치지 말고 `sb story edit`를 써요. 그래야 옛 목소리나 옛 그림이 남지 않아요.

| 하고 싶은 것 | 명령 | 일어나는 일 |
|---|---|---|
| 글 고치기 | `sb story edit <폴더> 3 --text "…"` | 그 쪽 목소리·글 자리를 비워요. 0쪽이면 제목도 바뀌어요 |
| 지시문 고치고 다시 그리기 | `sb story edit <폴더> 3 --prompt "…" --note "까닭"` | 그림을 지워요 → `sb draw` |
| 지시문은 그대로 다시 그리기 | `sb story edit <폴더> 3 --redraw --note "까닭"` | 그림을 지워요 → `sb draw` |
| 나오는 인물 바꾸기 | `sb story edit <폴더> 3 --cast child,toy1` | 그림을 지워요 |
