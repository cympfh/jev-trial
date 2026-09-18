#!/usr/bin/env python3
"""Play tic-tac-toe until it ends. Jev picks a legal cell for both sides."""
import json, os, sys, time, urllib.error, urllib.request

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)
LABELS = [str(i) for i in range(1, 10)]

def winner(board):
    for a, b, c in LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def draw_board(board):
    cells = [board[i] or LABELS[i] for i in range(9)]
    rows = [" ".join(cells[i:i + 3]) for i in (0, 3, 6)]
    return "\n".join(rows)

def ask(key, board, mark):
    empty = [LABELS[i] for i, v in enumerate(board) if not v]
    state = {
        "board": draw_board(board),
        "cells": "1 2 3 / 4 5 6 / 7 8 9, empty cells still show their number",
        "turn": mark,
        "legal": empty,
    }
    questions = {
        "cell": {
            "type": "choice",
            "instructions": (
                f"{mark} の番。目的は {mark} がこのゲームに勝つこと。"
                "勝てるマスがあればそれを取る。"
                "相手が次の手で勝つなら、それを止める。"
                "どちらでもなければ、自分の勝ちに一番近い最善手を選ぶ。"
                "候補は空いているマスだけ。すでに置いてあるマスは選ばない。"
            ),
            "criteria": {label: f"マス {label}" for label in empty},
        }
    }
    body = {"model": "jev-latest", "state": state, "questions": questions}
    req = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(body, ensure_ascii=False).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read().decode()
            status = res.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        status = e.code
    ms = int((time.perf_counter() - t) * 1000)
    parsed = json.loads(raw)
    return status, ms, parsed

def main() -> int:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set", file=sys.stderr)
        return 1
    pause = float(os.environ.get("TTT_PAUSE", "0"))
    board = [""] * 9
    mark = "X"
    log = []
    print("tic-tac-toe  X から。空マスの番号だけが候補。", flush=True)
    print(draw_board(board), flush=True)
    print(flush=True)
    while True:
        status, ms, parsed = ask(key, board, mark)
        answer = parsed.get("answers", {}).get("cell", {})
        cell = answer.get("choice")
        probs = answer.get("probabilities") or {}
        print(f"{mark}  status {status}  {ms} ms  -> {cell}  {probs.get(cell)}", flush=True)
        if status != 200 or cell not in LABELS:
            print(json.dumps(parsed, ensure_ascii=False, indent=2), flush=True)
            return 1
        i = LABELS.index(cell)
        if board[i]:
            print("illegal cell", cell, flush=True)
            return 1
        board[i] = mark
        print(draw_board(board), flush=True)
        print(flush=True)
        log.append({
            "mark": mark,
            "cell": cell,
            "ms": ms,
            "model": parsed.get("model"),
            "probabilities": probs,
            "confidence": answer.get("confidence"),
        })
        got = winner(board)
        if got or all(board):
            end = got or "draw"
            print(f"end: {end}", flush=True)
            out = {"end": end, "moves": log, "board": board}
            path = os.environ.get("TTT_OUT")
            if path:
                Path = __import__("pathlib").Path
                Path(path).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 0
        mark = "O" if mark == "X" else "X"
        if pause:
            time.sleep(pause)

if __name__ == "__main__":
    raise SystemExit(main())
