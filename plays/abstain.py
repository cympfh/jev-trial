#!/usr/bin/env python3
"""Abstain in code when the top choice is under 0.6."""
import json, os, sys, time, urllib.error, urllib.request

THRESHOLD = 0.6
CASES = [
    "注文が二つ届いた。余分な方を返金してください。",
    "届いた箱が凹んでいた。本当に腹が立つ。",
    "この料金、どういうこと？",
]
QUESTIONS = {
    "kind": {
        "type": "choice",
        "instructions": "この文の主な用件はどれか。返金を求めているか、文句だけか、どちらか判断できないか。",
        "criteria": {
            "refund": "お金を返してほしいと求めている",
            "complaint": "不満や文句だけで、返金は求めていない",
            "unclear": "返金か文句か、この文だけでは決められない",
        },
    }
}

def ask(key, text):
    body = {"model": "jev-latest", "state": text, "questions": QUESTIONS}
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
    return status, ms, json.loads(raw)

def main() -> int:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set", file=sys.stderr)
        return 1
    rows = []
    for text in CASES:
        status, ms, parsed = ask(key, text)
        answer = parsed.get("answers", {}).get("kind", {})
        choice = answer.get("choice")
        probs = answer.get("probabilities") or {}
        top = probs.get(choice)
        act = "abstain" if top is None or top < THRESHOLD else "act"
        print(f"{status} {ms} ms  {act}  {choice} {top}", flush=True)
        print(text, flush=True)
        print(flush=True)
        if status != 200:
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            return 1
        rows.append({
            "text": text,
            "ms": ms,
            "model": parsed.get("model"),
            "choice": choice,
            "probability": top,
            "probabilities": probs,
            "confidence": answer.get("confidence"),
            "action": act,
        })
    path = os.environ.get("ABSTAIN_OUT")
    if path:
        from pathlib import Path
        Path(path).write_text(json.dumps({"threshold": THRESHOLD, "rows": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
