"""원격 작업자 idle_min(기본 2분) 쉼 → 깨움 · 30분 안 두 번이면 ESCALATE(사용자 보고) · 진행표 10분 안이면 일하는 중 · 계정 한도는 따로.

사용: python idle_escalate.py project.json
상태는 `hc get --json` 을 먼저 본다(tools/hcstate.py). wake_owner 가 desk 가 아니면 깨우지 않고 경보만 낸다.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hcstate import pane_status  # noqa: E402

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
STATE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), f".idle-state-{cfg['name']}.json")
WINDOW, BUSY_MIN = 1800, 10
IDLE_SEC = 60 * int((cfg.get("idle_min") or {}).get("remote_worker", 2))
CAN_WAKE = cfg.get("wake_owner", "lead") == "desk"


def hc(*args: str) -> str:
    return subprocess.run(["hc", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60).stdout


def progress_age_min(remote: dict) -> int:
    cmd = f"[int]((Get-Date)-(Get-Item '{remote['progress']}').LastWriteTime).TotalMinutes"
    try:
        out = subprocess.run(["hc", "exec", "--on", remote["machine"], "powershell", "-NoProfile", "-Command", cmd],
                             capture_output=True, text=True, timeout=50).stdout.split()
        return int(out[-1])
    except Exception:
        return 999


def log_incident(line: str) -> None:
    with open(cfg["incidents_file"], "a", encoding="utf-8") as f:
        f.write(line + "\n")


try:
    state = json.load(open(STATE, encoding="utf-8"))
except Exception:
    state = {}

now = time.time()
out = []
for r in cfg["remotes"]:
    pane, label = r["worker"], r["label"]
    s = state.get(pane) or {"idle_since": None, "nudges": [], "woke": False, "reported": 0, "limit_logged": False}
    st = pane_status(pane)
    working = st == "working"
    limit = st == "LIMIT"
    dialog = st in ("DIALOG", "blocked")
    if st in ("SHELL_ONLY", "error"):
        out.append(f"{'CLAUDE_EXITED' if st == 'SHELL_ONLY' else 'ERROR'} {pane} {label}")
    s["nudges"] = [t for t in s["nudges"] if now - t < WINDOW]

    if working and not (limit or dialog):
        s.update(idle_since=None, woke=False, limit_logged=False)
    else:
        s["idle_since"] = s["idle_since"] or now
        idle = now - s["idle_since"]
        if limit:
            if not s["limit_logged"]:
                s["limit_logged"] = True
                log_incident(f"- [{time.strftime('%m-%d %H:%M')}] [갈래: 계정 한도] {label} {pane} · 조치: 그 PC 로그인(사람)")
            out.append(f"LIMIT {pane} {label}")
        elif dialog:
            out.append(f"DIALOG {pane} {label}")
        elif idle >= IDLE_SEC and not s["woke"] and progress_age_min(r) <= BUSY_MIN:
            out.append(f"BUSY {pane} {label}")
            s["idle_since"] = now
        elif idle >= IDLE_SEC and not s["woke"] and not CAN_WAKE:
            out.append(f"REMOTE_IDLE {pane} {label} {int(idle // 60)}m (wake_owner={cfg.get('wake_owner', 'lead')})")
        elif idle >= IDLE_SEC and not s["woke"]:
            hc("send", pane, f"[창구 감독] {label} {int(idle // 60)}분째 쉼 — 묶음 다음 줄 바로 · 진행표 한 줄 · 못 하면 [막힘] 까닭 한 줄")
            s["woke"] = True
            s["nudges"].append(now)
            out.append(f"WOKE {pane} {label} count30={len(s['nudges'])}")
            if len(s["nudges"]) >= 2 and now - s["reported"] > WINDOW:
                s["reported"] = now
                times = ", ".join(time.strftime("%H:%M", time.localtime(t)) for t in s["nudges"])
                log_incident(f"- [{time.strftime('%m-%d %H:%M')}] [갈래: 원장 있는데 대기] {label} {pane} · 깨움 {len(s['nudges'])}번({times}) · 까닭: (채움) · 조치: (채움) · 규칙 반영: (채움)")
                out.append(f"ESCALATE {pane} {label} at {times}")
    state[pane] = s

json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
print("\n".join(out) or "OK")
