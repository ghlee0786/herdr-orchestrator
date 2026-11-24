"""칸 상태(`hc get` 1차) + 원격 화면 판정 + 진행표 나이.

사용: python check.py project.json
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hcstate import pane_status  # noqa: E402

cfg = json.load(open(sys.argv[1], encoding="utf-8"))


def run(args: list, timeout: int = 100) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout).stdout
    except Exception:
        return ""


for r in cfg["remotes"]:
    for role in ("worker", "watch", "uiux"):
        st = pane_status(r[role])
        print(f"{r['label']} {role} {r[role]} | {st}")
    ps = (f"& '{r['shots']}\\screenwatch.ps1' -Dir '{r['shots']}' -AppLike '{cfg.get('app_process_like', '*')}' "
          f"-LoginMarker '{cfg.get('login_marker', '')}' -AuthWaitMarker '{cfg.get('auth_wait_marker', '')}'")
    screen = [l for l in run(["hc", "exec", "--on", r["machine"], "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps]).splitlines() if "SAME_MIN" in l]
    age = run(["hc", "exec", "--on", r["machine"], "powershell", "-NoProfile", "-Command",
               f"[int]((Get-Date)-(Get-Item '{r['progress']}').LastWriteTime).TotalMinutes"], 60).split()
    print(f"SCREEN {r['label']}: {screen[-1] if screen else '읽기 실패'} · PROGRESS {age[-1] if age else '?'}m ago")
