# 결정 기록

## 주고받는 꼴
- 요청: `[결정 요청 <id>] 질문 · 안 A/B · 근거(요구 절 · 사용자 원문)`
- 답: `[결정 <id>] 채택 <안> · 까닭 · 패턴 · 되돌림 가능 <예/아니오>`
- 사용자 몫: `[사용자 몫 <id>] 갈래(되돌릴 수 없음 / 현장 사실 / 기존 결정 충돌 / 큰 범위 / 대등한 두 안) · 질문`

## decisions.jsonl 한 줄
{"id":"D-001","at":"<ISO 시각>","from":"<칸>","question":"…","options":["A","B"],"chosen":"A","reason":"…","pattern":"추천안 기본","reversible":true,"escalated":false}

## pending-user.md(창구의 결정 대기 목록)
| id | 물은 것 | 언제 | 답 |
|---|---|---|---|
