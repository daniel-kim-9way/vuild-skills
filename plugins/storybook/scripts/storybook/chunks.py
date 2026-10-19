"""한 쪽의 글을 그림 위에 한 번에 하나씩 얹을 조각(문장)으로 나눈다. 앱 TextChunks와 같은 규칙이다.

  split("“귤이다!” 서준이가 외쳤어요. 뭉치도 웃었어요.")
  # => ["“귤이다!”", "서준이가 외쳤어요.", "뭉치도 웃었어요."]
"""
from __future__ import annotations

import re

# 문장 끝(. ! ? …) 뒤에 닫는 따옴표가 붙어 있으면 거기까지 한 문장이다
SENTENCE = re.compile(r"[^.!?…]*[.!?…]+[”\"’')]*|[^.!?…]+\Z")
MIN_LENGTH = 5
MAX_CHUNKS = 4


def split(text: str) -> list[str]:
    text = str(text or "")
    sentences = [s.strip() for s in SENTENCE.findall(text) if s.strip()]
    if not sentences:
        return [text.strip()]
    pieces: list[str] = []
    for sentence in sentences:
        # «아!»처럼 아주 짧은 조각은 앞 문장에 붙인다
        if pieces and len(sentence) < MIN_LENGTH:
            pieces[-1] = f"{pieces[-1]} {sentence}"
        else:
            pieces.append(sentence)
    # 조각이 너무 많으면 짧은 이웃끼리 묶는다
    while len(pieces) > MAX_CHUNKS:
        i = min(range(len(pieces) - 1), key=lambda j: len(pieces[j]) + len(pieces[j + 1]))
        pieces[i:i + 2] = [f"{pieces[i]} {pieces[i + 1]}"]
    return pieces


def for_page(page: dict) -> list[str]:
    """표지는 제목 한 덩어리, 본문은 문장마다"""
    return [str(page["text"]).strip()] if page["n"] == 0 else split(page["text"])
