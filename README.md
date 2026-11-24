# Herdr 오케스트레이터

여러 AI 코딩 칸(pane)을 한 사람의 지시 아래 돌려 **개발 → 리뷰 → 병합 → 배포 → 원격 시험**까지 쉬지 않고 이어 가는 운영 체계.
특정 프로젝트 · 언어 · 제품에 묶이지 않는다. 프로젝트마다 다른 것(저장소 · 시험 PC · 서버 · 요구사항 문서)은 **설정과 규칙 덧 파일**로만 붙인다.

| 문서 | 내용 |
|---|---|
| [docs/structure.md](docs/structure.md) | 도구 넷의 역할 · 세 가지 이름 · 칸 구조 · 정보가 흐르는 길 · 칸 띄우기 표준 · 함정 |
| [docs/roles.md](docs/roles.md) | 칸 역할 · 기본 강도 · 상주와 부름 · 결정 매니저 헌장 · 창구 |
| [docs/rules.md](docs/rules.md) | 공통 규칙(G 공통 · H 운영 · C 코드 · T 시험) — 허락 범위 · 일곱 갈래 · 실패 상한 · 끝 보고 재검증 |
| [docs/workflow.md](docs/workflow.md) | 요청 → 레인 → 리뷰 관문 → 빌드 자리 · 묶음 검사 → 병합 → 키트 · 설치기 · release → CI/CD → 원격 시험 · 총괄 상시 루프 |
| [docs/remote-testing.md](docs/remote-testing.md) | 원격 시험 PC 운영(머신 준비 · 칸 셋 · 앱 켜는 길 · 묶음 = 대본 · 스스로 깨기 · 시나리오 판 · 화면 판정 · 자리 등록부) |
| [docs/supervision.md](docs/supervision.md) | 깨우는 쪽 하나 · 감시견 경보 · 대기열 · 지시 장부 훅 · 판정 사다리 · 사건 장부 선순환 |
| [docs/recovery.md](docs/recovery.md) | 세션 연속성 · 칸 장부 · 복구 실행기 · 자동 되살림 · Core 재시작 · 재부팅 · 칸 닫기 |
| [docs/migration.md](docs/migration.md) | 표시 앱 이관 · 총괄 소유권 인계(ACK) · 다른 모델 사이 전환 · 계정 바꿈 |
| [templates/](templates) | 목표 파일 · 지시 장부 · 대기열 · 결정 기록 · 인계 · 상태 보고 · 한도 상태 · 묶음 · 시나리오 판 · 사건 장부 · 재개 글 · 프로젝트 설정 |
| [tools/](tools) | 감독 대본(설정 파일로 대상만 바꿔 씀) |

## 네 줄 요약
1. **사용자 원문이 가장 위**: 사용자 말은 원문 그대로 기록 · 전달하고, 그 원문이 모든 규칙보다 앞선다.
2. **일은 규칙과 함께 넘긴다**: 지시마다 「규칙 파일 + 걸리는 번호」 와 「업무」 를 같이 보낸다.
3. **멈추지 않는다 · 판정은 증거로**: 칸은 스스로 깨고, 멈춤은 `hc get` 상태 · 화면 · 진행표로 판정하고, 되풀이되면 사람에게 보고한 뒤 규칙을 고친다.
4. **같은 대화로 잇는다**: 끊기면 원래 대화 id · 레인으로 되살리고, 새로 시작하거나 목표를 복제하지 않는다.

## 프로젝트에 붙이는 법
1. `templates/project.example.json` 을 복사해 저장소 · 원격 PC · 진행표 경로 · 앱 프로세스 이름과 운영 값(`wake_owner` · `answer_route` · `idle_min` · `fail_cap` · `roles` · `approvals` · `build_slots`)을 채운다.
2. 프로젝트 고유 규칙은 `rules.<프로젝트>.md` 같은 덧 파일로 두고, 공통 규칙(`docs/rules.md`)을 고치지 않는다.
3. 원격 PC 마다 칸 셋을 띄우고 `docs/remote-testing.md` 대로 묶음을 넘긴다.
4. 감시는 `tools/` 대본을 그 설정 파일로 `wake_owner` 쪽에서 돌린다(LLM 칸에 주기 감시를 맡기지 않는다).
5. 칸 장부 · 목표 파일 · 지시 장부를 먼저 만들고, 복구 · 정리는 `docs/recovery.md` 대로 한다.
