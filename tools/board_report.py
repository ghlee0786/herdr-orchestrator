"""원격 시나리오 판을 모아 완료율 · 이전 대비 · 미완 줄을 표로(대화에 붙임).

사용: python board_report.py project.json
"""
import base64
import json
import os
import subprocess
import sys
import time

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
LAST = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), f".board-last-{cfg['name']}.json")
MARK = set("○●◯")


def fetch(machine: str, path: str) -> str:
    cmd = f"if(Test-Path '{path}'){{[Convert]::ToBase64String([IO.File]::ReadAllBytes('{path}'))}}"
    out = subprocess.run(["hc", "exec", "--on", machine, "powershell", "-NoProfile", "-Command", cmd],
                         capture_output=True, text=True, timeout=80).stdout
    try:
        return base64.b64decode("".join(out.split())).decode("utf-8-sig", errors="replace")
    except Exception:
        return ""


def rows(text: str):
    hdr = None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if "미진행" in cells and "완료" in cells:
            hdr = [cells.index("미진행"), cells.index("진행"), cells.index("완료")]
            continue
        if hdr and len(cells) > max(hdr) and not set("".join(cells)) <= set("-: "):
            k = next((i for i, j in enumerate(hdr) if any(ch in MARK for ch in cells[j])), None)
            if k is not None:
                yield k, cells, hdr


def pct(n: list) -> int:
    total = sum(n)
    return round(100 * n[2] / total) if total else 0


def delta(n: list, old) -> str:
    if not old:
        return "(이전 없음)"
    return f"(이전 {old[2]}/{sum(old)} → +{n[2] - old[2]} 완료 · {pct(n) - pct(old):+d}%p)"


try:
    prev = json.load(open(LAST, encoding="utf-8"))
except Exception:
    prev = {}

cur, open_rows = {}, []
for r in cfg["remotes"]:
    n = [0, 0, 0]
    for k, c, hdr in rows(fetch(r["machine"], r["board"])):
        n[k] += 1
        if k < 2:
            result = c[hdr[2] + 1] if len(c) > hdr[2] + 1 else ""
            open_rows.append(f"| {r['label']} | {c[0][:16]} | {c[1][:40]} | {'○' if k == 0 else ''} | {'○' if k == 1 else ''} | | {result[:40]} |")
    cur[r["label"]] = n

total = [sum(v[i] for v in cur.values()) for i in range(3)]
print(f"[판 30분 {time.strftime('%H:%M')} · 이전 {prev.get('_time', '-')}] 합계 완료율 {pct(total)}% ({total[2]}/{sum(total)}) {delta(total, prev.get('_all'))}")
for label, n in cur.items():
    print(f"- {label} {pct(n)}% ({n[2]}/{sum(n)}) {delta(n, prev.get(label))}")
print("\n| PC | 번호 | 시나리오 | 미진행 | 진행 | 완료 | 결과 |\n|---|---|---|:-:|:-:|:-:|---|")
print("\n".join(open_rows))
json.dump({**cur, "_all": total, "_time": time.strftime("%H:%M")}, open(LAST, "w", encoding="utf-8"), ensure_ascii=False)
