# LAB PILOT — Security Hardening 구현 계획

> 기반 스펙: SPEC-security.md  
> 작성일: 2026-04-27  
> Opus 리스크 분석 반영

---

## 실행 순서 (스펙 Phase와 차이 있음)

```
T1(0-B) → T2(0-A) → T3(0-C)
                         ↓
                       [Checkpoint 0]
                         ↓
              T4(1-A) ← 0-B, 0-C 완료 후만 시작
         T5(1-B) T6(1-C) T7(1-D) T8(1-E) ← 독립, 병렬 가능
                         ↓
                       [Checkpoint 1]
                         ↓
              T9(2-A) → T12(2-D)
              T10(2-B) ← T5(1-B) 완료 후
              T11(2-C) ← 독립
                         ↓
                       [Checkpoint 2]
```

**Opus 결정 사항 (모호했던 항목)**:
- 0-A: MAX_RETRIES 초과 시 → 앱 종료 없이 degraded mode (로그 에러 후 task 정리)
- 1-C: WS 에러 전송 포맷 → `{"type": "error", "code": "internal_error", "message": "..."}`
- 2-A: 역방향 전이 (진행중 → 계획중) 불허. `/start`는 logs 초기화 안 함
- 2-C: deadband 절대값 0.1g 고정, 채널별 분리 없음

---

## Phase 0 — 즉시 수정

### T1 — DB 커넥션 풀 명시 (0-B)

**목적**: token_version 도입(T4) 전 DB 부하 대비. 가장 빠른 단독 수정.

**수정 파일**: `lab-pilot-demo/backend/app/database.py`

**변경 내용**:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
)
```

**수락 기준**:
- [ ] `pool_size=20`, `max_overflow=10`, `pool_timeout=30` 명시
- [ ] 서버 시작 → `/api/health` 200 응답

---

### T2 — ws_manager_client 재시도 수정 (0-A)

**목적**: CancelledError 미처리로 인한 좀비 task 방지.

**수정 파일**: `ss_manager/core/ws_manager_client.py`

**변경 내용**:
- `MAX_RETRIES = 10`, `RETRY_BASE = 2` (최대 60초 cap)
- `_connect_loop` 내부: CancelledError → `return`, 일반 Exception → retry++
- retry == MAX_RETRIES → `logger.error` + `_tasks.pop(manager_id, None)` (degraded mode)
- 성공 연결 시 `retry = 0` 초기화

**수락 기준**:
- [ ] CancelledError 수신 시 함수가 정상 종료 (return)
- [ ] MAX_RETRIES(10) 초과 시 task가 종료되고 `_tasks`에서 제거됨
- [ ] 지수 백오프: 1회차 2s, 2회차 4s, ..., 6회차 이후 60s 상한 cap
- [ ] 연결 복구 후 retry 카운터 0으로 리셋

---

### T3 — Rate Limiting (0-C)

**목적**: 로그인/회원가입 brute force 차단. 1-A(/force-logout)보다 먼저 적용.

**수정 파일**:
- `lab-pilot-demo/backend/requirements.txt` — `slowapi` 추가
- `lab-pilot-demo/backend/app/main.py` — Limiter 등록
- `lab-pilot-demo/backend/app/api/auth.py` — 데코레이터 적용

**변경 내용**:
```python
# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

```python
# auth.py — Request 파라미터 추가 필수 (slowapi 요구사항)
from app.main import limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: UserLogin, db: ...):
    ...

@router.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, body: UserCreate, db: ...):
    ...
```

> ⚠️ **주의**: slowapi는 핸들러 함수 시그니처에 `request: Request`가 있어야 동작. 현재 auth.py에 없으면 추가 필요.

**수락 기준**:
- [ ] `pip install slowapi` (또는 requirements.txt 반영)
- [ ] 같은 IP에서 로그인 6회 연속 → 429 Too Many Requests
- [ ] 같은 IP에서 회원가입 4회 연속 → 429
- [ ] 서버 재시작 후 카운터 초기화 확인 (in-memory 특성)

---

### [Checkpoint 0]

> T1, T2, T3 모두 완료 후 확인

- [ ] `/api/health` 200
- [ ] 로그인 6회 → 429
- [ ] ss_manager 로그에서 "좀비 task" 없음 확인 (연결 끊기 테스트)

---

## Phase 1 — 중요 수정

### T4 — 강제 로그아웃 (token_version) (1-A)

> **고위험**: 순서 틀리면 기존 사용자 전원 401. T1(DB 풀), T3(Rate Limit) 완료 후 시작.

**수정 파일**:
- `lab-pilot-demo/backend/app/models/models.py`
- `lab-pilot-demo/backend/alembic/versions/0003_add_token_version.py` (신규)
- `lab-pilot-demo/backend/app/api/auth.py`
- `lab-pilot-demo/backend/app/dependencies.py`
- `lab-pilot-demo/backend/app/api/admin/users.py`

**변경 순서 (내부 의존성 — 순서 반드시 준수)**:

**Step 1** — 모델에 컬럼 추가:
```python
# models.py — User 클래스에 추가
token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
```

**Step 2** — Alembic 마이그레이션 작성 + 실행:
```python
# 0003_add_token_version.py
def upgrade():
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))

def downgrade():
    op.drop_column("users", "token_version")
```
```bash
alembic upgrade head
```

**Step 3** — JWT 발급에 `tv` 클레임 추가:
```python
# auth.py — _create_access_token 수정
def _create_access_token(user_id: int, token_version: int) -> str:
    payload = {
        "sub": str(user_id),
        "tv": token_version,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

**Step 4** — 검증에 `tv` 비교 추가:
```python
# dependencies.py — get_current_user 수정
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
user_id = payload.get("sub")
tv = payload.get("tv")
# ... user 조회 후
if tv is None or user.token_version != tv:
    raise credentials_exception
```

**Step 5** — 강제 로그아웃 엔드포인트:
```python
# admin/users.py 또는 별도 엔드포인트
@router.post("/users/{user_id}/force-logout", status_code=200)
async def force_logout(user_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    user.token_version += 1
    await db.commit()
    logger.info("[admin] 강제 로그아웃: target_user_id=%d", user_id)
    return {"message": "강제 로그아웃 완료"}
```

> ⚠️ **위험**: Step 3만 배포하고 Step 4 안 하면 기존 `tv` 없는 토큰들이 즉시 401.  
> Step 4에서 `tv is None` 케이스를 허용(pass)하고, 구 토큰 만료(7일) 후 제거하는 방식이 안전.  
> → `if tv is not None and user.token_version != tv: raise`로 점진적 적용 권장.

**수락 기준**:
- [ ] `alembic upgrade head` 성공
- [ ] 기존 로그인 토큰 → 계속 동작 (tv=None 호환)
- [ ] force-logout 후 신규 로그인 전 기존 토큰 → 401
- [ ] 관리자만 `/force-logout` 접근 가능 (일반 유저 → 403)
- [ ] `/force-logout`에도 Rate Limit 동작 (T3 완료로 자동 적용)

---

### T5 — 장치 명령 Enum 검증 (1-B)

**수정 파일**: `lab-pilot-demo/backend/app/schemas/schemas.py`, `app/api/devices.py`

**변경 내용**:
```python
# schemas.py
class BalanceCommand(str, Enum):
    tare = "tare"
    zero = "zero"

class FurnaceCommand(str, Enum):
    set_temperature = "set_temperature"
    stop = "stop"

class DeviceCommandRequest(BaseModel):
    device_type: Literal["balance", "furnace"]
    command: str
    params: dict[str, Any] = {}

    @model_validator(mode="after")
    def validate_command(self) -> "DeviceCommandRequest":
        allowed = {
            "balance": set(BalanceCommand),
            "furnace": set(FurnaceCommand),
        }
        if self.command not in {e.value for e in allowed[self.device_type]}:
            raise ValueError(f"허용되지 않은 명령: {self.command}")
        return self
```

**수락 기준**:
- [ ] `{"device_type": "balance", "command": "tare"}` → 200
- [ ] `{"device_type": "balance", "command": "rm -rf /"}` → 422
- [ ] `{"device_type": "furnace", "command": "tare"}` → 422 (타입 불일치)

---

### T6 — WebSocket 예외 처리 개선 (1-C)

**수정 파일**: `lab-pilot-demo/backend/app/api/ws.py`

**변경 내용**:
```python
# 기존 except Exception: pass → 타입별 분리
from fastapi import WebSocketDisconnect

except WebSocketDisconnect:
    logger.info("[WS] 클라이언트 정상 종료")
except asyncio.CancelledError:
    raise
except Exception as exc:
    logger.error("[WS] 예상치 못한 오류: %s", exc, exc_info=True)
    try:
        await websocket.send_json({
            "type": "error",
            "code": "internal_error",
            "message": "Internal server error",
        })
    except Exception:
        logger.debug("[WS] 에러 응답 전송 실패 (연결 끊김)")
```

**수락 기준**:
- [ ] 클라이언트 브라우저 탭 닫기 → 로그에 "정상 종료" 기록
- [ ] `asyncio.CancelledError` 발생 시 상위로 전파 (서버 정상 종료)
- [ ] 예외 발생 시 에러 로그 기록 (무음 실패 없음)

---

### T7 — 로그 파일 RotatingFileHandler (1-D)

**수정 파일**: `lab-pilot-demo/backend/app/core/logger.py`

**변경 내용**:
```python
from logging.handlers import RotatingFileHandler

# FileHandler → RotatingFileHandler
handler = RotatingFileHandler(
    file_path,
    maxBytes=50 * 1024 * 1024,  # 50MB
    backupCount=10,
    encoding="utf-8",
)
```

**수락 기준**:
- [ ] 로그 핸들러 타입이 `RotatingFileHandler`
- [ ] 기존 로그 파일 정상 기록 유지

---

### T8 — 캐시 asyncio.Lock per-key (1-E)

**수정 파일**: `ss_manager/core/ws_manager_client.py`

**변경 내용**:
```python
from collections import defaultdict

_cache: dict[int, ManagerCache] = {}
_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

async def update_cache(manager_id: int, data: ManagerCache) -> None:
    async with _locks[manager_id]:
        _cache[manager_id] = data

async def get_cache_item(manager_id: int) -> ManagerCache | None:
    async with _locks[manager_id]:
        return _cache.get(manager_id)

async def remove_cache(manager_id: int) -> None:
    async with _locks[manager_id]:
        _cache.pop(manager_id, None)
    _locks.pop(manager_id, None)  # Lock GC
```

> ⚠️ **Lock 내부에서 외부 I/O 금지** (SiLA2 gRPC 호출 불가). 캐시 read/write만.

**수락 기준**:
- [ ] 기존 `_cache` 직접 접근 코드 → `update_cache / get_cache_item / remove_cache` 함수 경유
- [ ] Lock GC: `remove_cache` 시 `_locks`에서도 제거

---

### [Checkpoint 1]

- [ ] T4~T8 전부 완료
- [ ] 전체 pytest 통과
- [ ] 강제 로그아웃 수동 테스트: 관리자 로그인 → force-logout → 기존 토큰 401

---

## Phase 2 — 설계 개선

### T9 — Workflow 상태 머신 (2-A)

> **고위험**: 기존 DB에 비정상 status 값 있으면 조회 500. 마이그레이션 전 데이터 확인 필수.

**신규 파일**: `lab-pilot-demo/backend/app/core/workflow_state.py`

**수정 파일**: `lab-pilot-demo/backend/app/api/workflows.py`

**사전 확인** (구현 전):
```sql
-- DB에서 비표준 status 값 확인
SELECT DISTINCT status FROM workflows;
```

**구현 내용**:
```python
# workflow_state.py
from enum import Enum

class WorkflowStatus(str, Enum):
    planning = "계획중"
    in_progress = "진행중"
    completed = "완료"

VALID_TRANSITIONS = {
    WorkflowStatus.planning: {WorkflowStatus.in_progress},
    WorkflowStatus.in_progress: {WorkflowStatus.completed},
    WorkflowStatus.completed: set(),
}

def assert_transition(current: WorkflowStatus, target: WorkflowStatus) -> None:
    if target not in VALID_TRANSITIONS.get(current, set()):
        raise ValueError(f"잘못된 상태 전이: {current.value} → {target.value}")

async def assert_logs_completed(db: AsyncSession, workflow_id: int) -> None:
    result = await db.execute(
        select(ExperimentLog).where(
            ExperimentLog.workflow_id == workflow_id,
            ExperimentLog.status != "완료",
        )
    )
    incomplete = result.scalars().all()
    if incomplete:
        raise ValueError(f"미완료 로그 {len(incomplete)}건이 있습니다")
```

**workflows.py 추가**:
```python
# /start 엔드포인트 (계획중 → 진행중)
@router.post("/{workflow_id}/start", response_model=WorkflowResponse)
async def start_workflow(workflow_id: int, ...):
    ...
    assert_transition(WorkflowStatus(workflow.status), WorkflowStatus.in_progress)
    workflow.status = WorkflowStatus.in_progress.value
    ...

# /complete 전에 logs 완료 검증 추가
async def complete_workflow(workflow_id: int, ...):
    ...
    await assert_logs_completed(db, workflow_id)
    assert_transition(WorkflowStatus(workflow.status), WorkflowStatus.completed)
    ...

# update_workflow에서 status 직접 변경 차단
if body.status is not None:
    assert_transition(WorkflowStatus(workflow.status), WorkflowStatus(body.status))
    workflow.status = body.status
```

**수락 기준**:
- [ ] DB에 표준 status 값만 존재 확인 (사전 확인)
- [ ] `계획중` workflow에 `/complete` → 400
- [ ] `완료` workflow에 `/start` → 400
- [ ] 미완료 로그 있는 `/complete` → 400 (미완료 건수 포함)
- [ ] 정상 흐름: `/start` → `/complete` → 200

---

### T10 — Workflow.data Pydantic 스키마 (2-B)

> **고위험**: 기존 JSONB data가 스키마 위반이면 조회 500. T5(1-B) 완료 후 진행.

**신규 파일**: `lab-pilot-demo/backend/app/schemas/workflow_data.py`

**사전 확인** (구현 전):
```sql
-- data 필드 샘플 확인
SELECT data FROM workflows LIMIT 10;
```

```python
# workflow_data.py
class Composition(BaseModel):
    oxide: str
    mol_fraction: float

class Step(BaseModel):
    step_type: Literal["칭량", "혼합", "소성", "분석"]
    order: int
    params: dict[str, Any] = {}

class WorkflowData(BaseModel):
    model_config = ConfigDict(extra="allow")  # 기존 데이터 호환
    compositions: list[Composition] = []
    steps: list[Step] = []
```

> `extra="allow"` 로 기존 데이터 호환성 확보. 안정화 후 제거 가능.

**연관 수정**:
- `schemas.py`: `WorkflowCreate.data` → `WorkflowData` 타입
- `models.py`: TypeDecorator는 **이번 단계에서 제외** (리스크 과대). `schemas.py`에서 입력 검증만.

**수락 기준**:
- [ ] 기존 workflow 조회 → 500 없음
- [ ] 새 workflow 생성 시 data 스키마 검증
- [ ] 잘못된 step_type → 422

---

### T11 — WS deadband 적용 (2-C)

**수정 파일**: `lab-pilot-demo/backend/app/api/ws.py`

```python
DEADBAND = 0.1  # g 단위, 이 미만 변화 전송 생략
_last_weight: float | None = None

# 폴링 루프 내
value = _find_balance_value()
if value is not None:
    if _last_weight is None or abs(value - _last_weight) >= DEADBAND:
        await websocket.send_json({"type": "weight", "value": value})
        _last_weight = value
```

> `_last_weight`는 WebSocket 연결 별 로컬 변수로 선언 (전역 아님).

**수락 기준**:
- [ ] 무게 변화 0.05g → 전송 없음
- [ ] 무게 변화 0.15g → 전송 있음
- [ ] 연결 끊기 후 재연결 시 `_last_weight` 초기화 (로컬 변수이므로 자동)

---

### T12 — N+1 쿼리 joinedload (2-D)

> T9(Workflow 상태 머신) 완료 후 진행. 쿼리 패턴이 T9에서 확정됨.

**수정 파일**: `lab-pilot-demo/backend/app/api/workflows.py`

```python
from sqlalchemy.orm import joinedload, selectinload

# list_workflows
result = await db.execute(
    select(Workflow)
    .options(joinedload(Workflow.owner))
    .where(...)
    .order_by(Workflow.created_at.desc())
)

# get_workflow (로그 포함 조회 시)
result = await db.execute(
    select(Workflow)
    .options(
        joinedload(Workflow.owner),
        selectinload(Workflow.logs),
    )
    .where(Workflow.workflow_id == workflow_id)
)
```

**수락 기준**:
- [ ] workflow 목록 조회 쿼리 수: N+1 → 1~2로 감소 (SQLAlchemy echo=True로 확인)
- [ ] 응답 데이터 동일

---

### [Checkpoint 2]

- [ ] T9~T12 전부 완료
- [ ] 전체 pytest 통과
- [ ] 수동 테스트: workflow 전체 상태 흐름 (계획중 → 진행중 → 완료)
- [ ] DB에 비정상 status 값 없음 확인

---

## 파일 변경 요약

| 파일 | 태스크 | 변경 유형 |
|------|--------|-----------|
| `backend/app/database.py` | T1 | 수정 |
| `ss_manager/core/ws_manager_client.py` | T2, T8 | 수정 |
| `backend/requirements.txt` | T3 | 수정 |
| `backend/app/main.py` | T3 | 수정 |
| `backend/app/api/auth.py` | T3, T4 | 수정 |
| `backend/app/models/models.py` | T4 | 수정 |
| `backend/alembic/versions/0003_add_token_version.py` | T4 | 신규 |
| `backend/app/dependencies.py` | T4 | 수정 |
| `backend/app/api/admin/users.py` | T4 | 수정 |
| `backend/app/schemas/schemas.py` | T5, T10 | 수정 |
| `backend/app/api/devices.py` | T5 | 수정 |
| `backend/app/api/ws.py` | T6, T11 | 수정 |
| `backend/app/core/logger.py` | T7 | 수정 |
| `backend/app/core/workflow_state.py` | T9 | 신규 |
| `backend/app/api/workflows.py` | T9, T12 | 수정 |
| `backend/app/schemas/workflow_data.py` | T10 | 신규 |
