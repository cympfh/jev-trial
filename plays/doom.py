#!/usr/bin/env python3
"""One Doom tick. Structured state only, no pixels."""
import json, os, sys, time, urllib.error, urllib.request

STATE = {
    "health": 28,
    "ammo": 4,
    "facing": "north",
    "enemy": {"kind": "imp", "distance_m": 14, "angle_deg": 35, "in_sight": True},
    "door": {"ahead": True, "distance_m": 2, "closed": True, "leads_to": "cover"},
}
QUESTIONS = {
    "action": {
        "type": "choice",
        "instructions": "この1ティックで取る行動はどれか。敵は正面ではなく、弾は少ない。ドアは目の前で、先は遮蔽。",
        "criteria": {
            "turn_left": "左を向く",
            "turn_right": "右を向く",
            "forward": "まっすぐ進む",
            "shoot": "撃つ",
            "open_door": "目の前のドアを開ける",
        },
    },
    "danger": {
        "type": "score",
        "instructions": "今この場の危険はどのくらい強いか。",
        "criteria": [
            "脅威はない",
            "見えているがすぐではない",
            "今撃たないと危ない",
            "もう被弾している",
        ],
    },
    "in_front": {
        "type": "noul",
        "instructions": "`enemy` は正面（angle が小さい）かつ届く距離にいるか。",
        "criteria": {
            "true": "正面で、今の武器が届く",
            "false": "横か、遠いか、見えていない",
        },
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
    print(f"status {status}  {ms} ms")
    try:
        print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(raw)
    return 0 if status == 200 else 1

if __name__ == "__main__":
    raise SystemExit(main())
