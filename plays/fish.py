#!/usr/bin/env python3
"""One Jev call: does 「魚は今夜歌っている」 follow from the premises?"""
import json, os, sys, time, urllib.error, urllib.request

STATE = "魚は空を飛ぶ。空を飛ぶものは月を歌う。月は今夜歌っている。"
QUESTIONS = {
    "fish_sings": {
        "type": "noul",
        "instructions": "この前提だけから、「魚は今夜歌っている」は出るか。前提にない知識は使わない。",
    },
    "moon_is_fish": {
        "type": "noul",
        "instructions": "この前提だけから、「月は魚である」は出るか。",
    },
    "trick": {
        "type": "choice",
        "instructions": "この文章の論理の型はどれか。",
        "criteria": {
            "chain": "前提を二つ繋げば結論が出る連鎖",
            "contradiction": "前提同士がぶつかっている",
            "missing": "結論に必要な前提が足りない",
            "not_a_puzzle": "パズルになっていない",
        },
    },
    "poem": {
        "type": "score",
        "instructions": "教科書の三段論法と比べて、どれくらいポエムか。",
        "criteria": [
            "教科書の三段論法そのもの",
            "名前だけ変わった三段論法",
            "ポエムだが論理は直線",
            "ポエムで、論理も少しずれている",
        ],
    },
}

def main() -> int:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("TYPESAFE_API_KEY is not set", file=sys.stderr)
        return 1
    body = {"model": "jev-latest", "state": STATE, "questions": QUESTIONS}
    req = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(body, ensure_ascii=False).encode(),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
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
    print(f"status {status}  {ms} ms")
    try:
        print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(raw)
    return 0 if status == 200 else 1

if __name__ == "__main__":
    raise SystemExit(main())
