# tools

모두 프로젝트 설정 파일 하나(`templates/project.example.json` 꼴)로 대상만 바꿔 쓴다. 프로젝트 고유 값은 대본에 넣지 않는다.
칸 상태는 `hc get --json` 의 `status.state` 를 1차 근거로 쓰고(`hcstate.py`), 화면 글은 한도 · 확인 창을 가릴 때만 보조로 쓴다.

| 대본 | 어디서 | 주기 | 하는 일 |
|---|---|---|---|
| `hcstate.py` | (모듈) | — | working · idle · done · blocked · error · DIALOG · LIMIT · SHELL_ONLY(에이전트 빠짐) 판정 |
| `screenwatch.ps1` | 각 원격 PC(설정의 `shots` 폴더에 둠 · UTF-8 BOM) | 호출될 때 | 화면 그대로 분 · 로그인 창 · 인증 기다림 · 앱 응답 |
| `idle_escalate.py project.json` | `wake_owner` 쪽 | 2분 | `idle_min` 쉼 깨움(`wake_owner: desk` 일 때만 보냄, 아니면 `REMOTE_IDLE` 경보만) · 30분 안 두 번 보고 · 한도 따로 · 진행표 10분 안이면 일하는 중 · `CLAUDE_EXITED` · `ERROR` |
| `check.py project.json` | `wake_owner` 쪽 | 4분 | 칸 상태 + 화면 판정 + 진행표 나이 |
| `board_report.py project.json` | 창구 · 총괄 | 30분 | 시나리오 판 완료율 · 이전 대비 · 미완 줄 표 |

필요: `hc`(Herdr Core) · Python 3.9+ · 원격 PC PowerShell 5+.

## 문서에만 있는 장치(직접 만들어 붙일 것)
아래는 운영에서 쓰는 장치로 문서에 동작이 정해져 있다. 환경마다 경로 · 셸 · 예약 방식이 달라 대본은 싣지 않았다.

| 장치 | 문서 | 바깥으로 뺄 값 |
|---|---|---|
| 원클릭 복구 실행기 | [recovery.md](../docs/recovery.md) | hc · App 경로 · 명부 · 대기 시간 · 잠금 이름 |
| 칸 장부 · 자동 되살림(Heal) | recovery.md | 장부 경로 · 총괄 · 믿는 폴더 · 되살림 차례 |
| Core 재시작 전후 대조 | recovery.md | 장부 연동 |
| 감시견(1분 · 경보 표) | [supervision.md](../docs/supervision.md) | 총괄 · 창구 · `idle_min` · 메모리 기준 |
| 대기열 기록 · 지시 장부 훅 | supervision.md | 폴더 · 꼬리표 정규식 · 시간대 |
| 칸 정리(쉬는 칸 닫기) | recovery.md | 보호 목록 · 쉼 분 |
| 시한 원복 고리 | [rules.md](../docs/rules.md) H-14 | 기한 · 원복 명령 · 알림 대상 |
| 원격 SSH 준비 · 스페이스 지킴이 | [remote-testing.md](../docs/remote-testing.md) | 사용자 · 공개키 · 허용 주소 |
| 대본 함수 이름 · 별칭 겹침 검사 | [structure.md](../docs/structure.md) 「함정」 | — |
