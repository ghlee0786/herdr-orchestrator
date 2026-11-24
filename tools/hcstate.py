"""칸 상태 판정 — `hc get --json` 의 status 를 1차 근거로, 화면 글은 보조로만.

반환 값: working · idle · done · blocked · error · DIALOG · LIMIT · SHELL_ONLY(에이전트 빠짐) · UNKNOWN
"""
import json
import re
import subprocess

SHELLS = ("powershell", "pwsh", "cmd", "bash", "sh", "zsh", "fish")
LIMIT_RE = re.compile(r"weekly limit|hit your .*limit|usage-credits", re.I)
DIALOG_RE = re.compile(r"What do you want to do|Enter to confirm|trust this folder", re.I)


def hc(*args: str, timeout: int = 60) -> str:
    try:
        return subprocess.run(["hc", *args], capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout).stdout
    except Exception:
        return ""


def pane_status(pane: str) -> str:
    try:
        d = json.loads(hc("get", "--json", pane, timeout=30))
    except Exception:
        return "UNKNOWN"
    fg = (d.get("foreground") or {}).get("name") or ""
    if d.get("state") == "live" and fg and fg.lower().removesuffix(".exe") in SHELLS:
        return "SHELL_ONLY"
    st = ((d.get("status") or {}).get("state") or "").lower()
    if st == "working":
        return "working"
    # 보조: 멈춰 보이는 칸만 화면 글로 한도 · 확인 창을 가린다
    tail = "\n".join(hc("read", pane, timeout=30).strip().splitlines()[-6:])
    if LIMIT_RE.search(tail):
        return "LIMIT"
    if st == "blocked" or DIALOG_RE.search(tail):
        return "DIALOG" if st != "blocked" else "blocked"
    return st or "UNKNOWN"
