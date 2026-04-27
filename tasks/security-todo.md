# LAB PILOT — Security Hardening Todo

> 상세 내용: tasks/security-plan.md  
> 기반 스펙: SPEC-security.md

---

## Phase 0 — 즉시 수정

- [ ] **T1** `database.py` — DB 커넥션 풀 명시 (pool_size=20, max_overflow=10, pool_timeout=30)
- [ ] **T2** `ws_manager_client.py` — 재시도 수정 (CancelledError, MAX_RETRIES=10, 지수 백오프)
- [ ] **T3** `main.py` + `auth.py` — slowapi Rate Limiting (로그인 5/min, 회원가입 3/min)

**[Checkpoint 0]** health + 429 + ss_manager 좀비 task 없음 확인

---

## Phase 1 — 중요 수정

- [ ] **T4** `models.py` + `0003 migration` + `auth.py` + `dependencies.py` + `admin/users.py` — token_version 강제 로그아웃 ⚠️ 고위험
  > **대응**: Step 순서 반드시 준수 → ① 모델 컬럼 추가(server_default="0") → ② alembic upgrade head → ③ _create_access_token에 tv 클레임 추가 → ④ get_current_user에 tv 검증 추가
  > **핵심**: Step ④에서 `if tv is not None and user.token_version != tv` 조건으로 작성할 것. `tv is None`이면 통과시켜야 기존 토큰(tv 없음) 사용자가 즉시 401 되지 않음. 기존 토큰은 7일 만료 후 자연 소멸.
- [ ] **T5** `schemas.py` + `devices.py` — 장치 명령 Enum 검증 (BalanceCommand, FurnaceCommand)
- [ ] **T6** `ws.py` — WebSocket 예외 처리 타입별 분리 (무음 실패 제거)
- [ ] **T7** `logger.py` — RotatingFileHandler (50MB, backupCount=10)
- [ ] **T8** `ws_manager_client.py` — asyncio.Lock per-key 캐시 동시성 보호

**[Checkpoint 1]** pytest 전체 통과 + 강제 로그아웃 수동 테스트

---

## Phase 2 — 설계 개선

- [ ] **T9** `workflow_state.py` (신규) + `workflows.py` — 상태 머신 + /start + logs 검증 ⚠️ 고위험
  > **구현 전 필수**: `SELECT DISTINCT status FROM workflows;` 실행해서 "계획중"/"진행중"/"완료" 외 다른 값이 없는지 확인. 비표준 값 있으면 먼저 데이터 정리 후 진행.
  > **대응**: `update_workflow`에서 status 직접 덮어쓰기 → `assert_transition()` 경유로 변경. 역방향 전이(진행중 → 계획중) 불허. `/start` 엔드포인트는 logs 초기화 안 함.
- [ ] **T10** `workflow_data.py` (신규) + `schemas.py` — Workflow.data Pydantic 스키마 ⚠️ 고위험
  > **구현 전 필수**: `SELECT data FROM workflows LIMIT 20;` 실행해서 실제 data 구조 확인. 스키마 정의 전에 필드명·타입 파악 필요.
  > **대응**: `WorkflowData`에 `model_config = ConfigDict(extra="allow")` 반드시 추가. 기존 JSONB에 예상 외 필드가 있어도 500 안 남. 안정화 후 extra="allow" 제거 가능. models.py TypeDecorator는 이번 단계 제외(리스크 과대), schemas.py 입력 검증만.
- [ ] **T11** `ws.py` — WS deadband 0.1g (last_value 로컬 변수)
- [ ] **T12** `workflows.py` — N+1 쿼리 joinedload 적용 (T9 완료 후)

**[Checkpoint 2]** pytest 전체 통과 + workflow 상태 흐름 수동 테스트
