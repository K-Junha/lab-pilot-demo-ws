# LAB PILOT — Security Hardening Specification

> 작성일: 2026-04-27  
> 환경: 연구실 내부망 (외부 접근 없음)  
> 스택: FastAPI (async, single worker) + PostgreSQL + Vue 3 + Electron  
> 인증: JWT 7일 단일 토큰 (리프레시 토큰 없음)  
> 상태: Draft

---

## 1. Objective

### 무엇을 고치는가

2026-04-27 코드 리뷰에서 발견된 보안 및 안정성 이슈를 **P0 → P1 → P2** 순서로 순차 수정한다.  
각 단계는 독립적으로 머지 가능하도록 설계한다.

### 범위

- **백엔드** (`lab-pilot-demo/backend`): Rate Limiting, 토큰 버전, 장치 명령 검증, 상태 전이, WS 예외 처리, DB 풀, 로그 로테이션
- **ss_manager** (`ss_manager/core`): ws_manager_client 재시도, 캐시 동시성
- **운영 플랜 문서화**: HTTPS 전환 시나리오 (현 단계 구현 제외)

### 범위 외

- 리프레시 토큰 도입
- HTTPS 실제 구현 (문서화만)
- Microservices 분리
- 모니터링/APM 연동

### 전제 조건 (Opus 결정)

| 항목 | 결정 |
|------|------|
| uvicorn 워커 수 | **단일 워커 (`--workers 1`)** — Rate Limit in-memory, asyncio.Lock 유효성 기준 |
| Rate Limiting 백엔드 | **slowapi + in-memory** (단일 워커 전제) |
| 장치 명령 검증 | **Enum 클래스** (코드 내장, Pydantic 자동 422) |
| 강제 로그아웃 | **User.token_version 컬럼** |
| 캐시 동시성 | **asyncio.Lock per-key** |
| Workflow 상태 머신 | **Enum + 전이 검증 함수** (`workflow_state.py`) |
| HTTPS | **플랜 문서화만** (self-signed 미적용) |

---

## 2. 수정 항목 상세

### Phase 0 — 즉시 수정 (P0 + Rate Limiting 합산)

> 의존성 없음. 한 번에 머지 가능.

#### 0-A. ws_manager_client 재시도 로직 수정

**파일**: `ss_manager/core/ws_manager_client.py`

**문제**: CancelledError 미처리 → 무한 루프, 좀비 task 누적

**수정 내용**:
```python
MAX_RETRIES = 10
RETRY_BASE = 2  # 지수 백오프: 2^n 초, 최대 60초

async def _connect_loop(manager_id: int):
    retry = 0
    while retry < MAX_RETRIES:
        try:
            await _connect(manager_id)
            retry = 0  # 성공 시 초기화
        except asyncio.CancelledError:
            logger.info("[ws_manager] task 취소: manager_id=%d", manager_id)
            return  # 정상 종료
        except Exception as exc:
            delay = min(RETRY_BASE ** retry, 60)
            logger.warning("[ws_manager] 재시도 %d/%d: manager_id=%d error=%s — %ds 후", 
                           retry + 1, MAX_RETRIES, manager_id, exc, delay)
            await asyncio.sleep(delay)
            retry += 1
    logger.error("[ws_manager] 최대 재시도 초과: manager_id=%d", manager_id)
    _tasks.pop(manager_id, None)
```

**검증**: manager 연결 끊었을 때 task가 MAX_RETRIES 후 종료되는지 로그 확인

---

#### 0-B. DB 커넥션 풀 명시

**파일**: `lab-pilot-demo/backend/app/database.py`

**수정 내용**:
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

**검증**: 서버 시작 후 `/api/health` 응답 확인

---

#### 0-C. Rate Limiting (로그인/회원가입)

**라이브러리 추가**: `slowapi`

**파일**: `lab-pilot-demo/backend/app/main.py`, `app/api/auth.py`

**수정 내용**:

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
# auth.py
@router.post("/login")
@limiter.limit("5/minute")          # IP당 1분에 5회
async def login(request: Request, ...):
    ...

@router.post("/register")
@limiter.limit("3/minute")          # IP당 1분에 3회
async def register(request: Request, ...):
    ...
```

**검증**: 6번 연속 로그인 시도 → 429 반환 확인

---

### Phase 1 — 중요 수정

> Phase 0 완료 후 진행. 항목별 독립 머지 가능.

#### 1-A. 강제 로그아웃 (token_version)

**파일**: `lab-pilot-demo/backend/app/models/models.py`, `app/dependencies.py`, `app/api/admin/users.py`

**DB 마이그레이션**: `alembic/versions/0003_add_token_version.py`

**수정 내용**:
```python
# models.py — User 모델에 컬럼 추가
token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

# JWT 발급 시 tv 클레임 포함
def create_token(user: User) -> str:
    payload = {
        "sub": str(user.user_id),
        "tv": user.token_version,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

# 검증 시 token_version 비교
async def get_current_user(token: str, db: AsyncSession) -> User:
    payload = jwt.decode(...)
    user = await db.get(User, payload["sub"])
    if user.token_version != payload.get("tv"):
        raise HTTPException(401, "토큰이 만료되었습니다. 다시 로그인하세요.")
    return user

# 강제 로그아웃 엔드포인트 (admin only)
@router.post("/users/{user_id}/force-logout")
async def force_logout(user_id: int, db: AsyncSession, _: User = Depends(require_admin)):
    await db.execute(
        update(User)
        .where(User.user_id == user_id)
        .values(token_version=User.token_version + 1)
    )
    await db.commit()
```

**주의**: 모든 인증 요청에 User 행 조회 추가됨. 성능 측정 후 이슈 없으면 캐시 불필요 (내부망 트래픽 낮음).

**검증**: 강제 로그아웃 후 기존 토큰으로 API 요청 → 401 확인

---

#### 1-B. 장치 명령 Enum 검증

**파일**: `lab-pilot-demo/backend/app/api/devices.py`, `app/schemas/schemas.py`

**수정 내용**:
```python
# schemas.py
from enum import Enum

class BalanceCommand(str, Enum):
    tare = "tare"
    zero = "zero"

class FurnaceCommand(str, Enum):
    set_temperature = "set_temperature"
    stop = "stop"

class DeviceCommandRequest(BaseModel):
    device_type: Literal["balance", "furnace"]
    command: str  # 타입별로 분기
    params: dict[str, Any] = {}

    @model_validator(mode="after")
    def validate_command(self):
        if self.device_type == "balance":
            BalanceCommand(self.command)  # 유효하지 않으면 ValueError → 422
        elif self.device_type == "furnace":
            FurnaceCommand(self.command)
        return self
```

**검증**: 허용되지 않은 command 값 전송 → 422 반환 확인

---

#### 1-C. WebSocket 예외 처리 개선

**파일**: `lab-pilot-demo/backend/app/api/ws.py`

**수정 내용**:
```python
# 현재 (문제)
except Exception:
    pass  # 무음 실패

# 개선
except WebSocketDisconnect:
    logger.info("[WS] 클라이언트 정상 종료")
except asyncio.CancelledError:
    raise  # task 취소는 전파
except Exception as exc:
    logger.error("[WS] 예상치 못한 오류: %s", exc, exc_info=True)
    try:
        await websocket.send_json({"type": "error", "message": "Internal server error"})
    except Exception:
        logger.debug("[WS] 에러 전송 실패 (연결 이미 끊김)")
```

**검증**: WebSocket 강제 끊기 → 로그에 "정상 종료" 기록 확인

---

#### 1-D. 로그 파일 로테이션

**파일**: `lab-pilot-demo/backend/app/core/logger.py`

**수정 내용**:
```python
from logging.handlers import RotatingFileHandler

# 현재
handler = logging.FileHandler(file_path, encoding="utf-8")

# 개선
handler = RotatingFileHandler(
    file_path,
    maxBytes=50 * 1024 * 1024,  # 50MB
    backupCount=10,
    encoding="utf-8",
)
```

**검증**: 로그 파일 50MB 초과 시 `.1`, `.2` 순번 파일 생성 확인

---

#### 1-E. 캐시 동시성 보호

**파일**: `ss_manager/core/ws_manager_client.py`

**수정 내용**:
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

**검증**: 동시 연결/해제 상황에서 KeyError 없음 확인

---

### Phase 2 — 설계 개선

> Phase 1 완료 후 진행. 각 항목 별도 PR.

#### 2-A. Workflow 상태 머신 + 전이 검증

**신규 파일**: `lab-pilot-demo/backend/app/core/workflow_state.py`

```python
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.models import Workflow, ExperimentLog

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
        raise ValueError(f"잘못된 상태 전이: {current} → {target}")

async def assert_logs_completed(logs: list["ExperimentLog"]) -> None:
    incomplete = [l for l in logs if l.status != "완료"]
    if incomplete:
        raise ValueError(f"미완료 로그 {len(incomplete)}건이 있습니다.")
```

**연관 수정**:
- `workflows.py`: `/start` 엔드포인트 추가 (계획중 → 진행중)
- `workflows.py`: `/complete` 전에 `assert_logs_completed()` 호출
- `models.py`: `Workflow.status` 컬럼 타입을 `WorkflowStatus` Enum으로 변경

**검증**:
- 완료 상태 workflow에 start 요청 → 400 확인
- 미완료 로그 있는데 complete 요청 → 400 확인

---

#### 2-B. Workflow.data Pydantic 스키마 정의

**신규 파일**: `lab-pilot-demo/backend/app/schemas/workflow_data.py`

```python
class Composition(BaseModel):
    oxide: str
    mol_fraction: float

class Step(BaseModel):
    step_type: Literal["칭량", "혼합", "소성", "분석"]
    order: int
    params: dict[str, Any] = {}

class WorkflowData(BaseModel):
    compositions: list[Composition] = []
    steps: list[Step] = []
```

**연관 수정**:
- `models.py`: `Workflow.data` → TypeDecorator로 WorkflowData 자동 직렬화
- `schemas.py`: `WorkflowCreate.data` → `WorkflowData` 타입

---

#### 2-C. WebSocket 폴링 개선 (deadband)

**파일**: `lab-pilot-demo/backend/app/api/ws.py`

```python
DEADBAND = 0.1  # 0.1g 미만 변화는 전송 생략

last_value: float | None = None

while True:
    await asyncio.sleep(POLL_INTERVAL)
    value = _find_balance_value()
    if value is not None and (last_value is None or abs(value - last_value) >= DEADBAND):
        await websocket.send_json({"type": "weight", "value": value})
        last_value = value
```

---

#### 2-D. N+1 쿼리 개선

**파일**: `lab-pilot-demo/backend/app/api/workflows.py`

```python
# 현재: lazy loading
result = await db.execute(select(Workflow).order_by(...))

# 개선: joinedload
from sqlalchemy.orm import joinedload

result = await db.execute(
    select(Workflow)
    .options(joinedload(Workflow.owner))  # User 미리 로드
    .order_by(Workflow.created_at.desc())
)
```

---

## 3. 파일 변경 목록

```
lab-pilot-demo/backend/
├── app/
│   ├── main.py                          # slowapi 등록
│   ├── database.py                      # pool_size 명시
│   ├── dependencies.py                  # token_version 검증 추가
│   ├── core/
│   │   ├── logger.py                    # RotatingFileHandler
│   │   └── workflow_state.py            # [신규] 상태 머신
│   ├── models/
│   │   └── models.py                    # token_version 컬럼
│   ├── schemas/
│   │   ├── schemas.py                   # DeviceCommandRequest Enum
│   │   └── workflow_data.py             # [신규] WorkflowData
│   └── api/
│       ├── auth.py                      # @limiter.limit 데코레이터
│       ├── devices.py                   # Enum 검증 적용
│       ├── ws.py                        # 예외 처리 + deadband
│       ├── workflows.py                 # /start 엔드포인트, logs 검증
│       └── admin/users.py               # /force-logout 엔드포인트
├── alembic/versions/
│   └── 0003_add_token_version.py        # [신규] 마이그레이션
└── requirements.txt                     # slowapi 추가

ss_manager/core/
├── ws_manager_client.py                 # 재시도 + asyncio.Lock
```

---

## 4. 코드 스타일

- 기존 코드 컨벤션 유지 (한국어 docstring, snake_case)
- Enum 값은 실제 DB 저장값과 동일 (한국어 문자열)
- 새 파일은 기존 파일 import 방식(`from app.core.xxx import ...`) 따름
- 타입 힌트 필수 (함수 인자, 반환값)
- `Any` 타입은 schema 정의 이후 단계적으로 제거
- 주석은 WHY만 (WHAT은 코드로)

---

## 5. 테스트 전략

> 이번 스펙에서는 전략만 정의. 실제 테스트 작성은 별도 진행.

### 단위 테스트 대상

| 항목 | 테스트 케이스 |
|------|-------------|
| `workflow_state.py` | 유효 전이 OK, 무효 전이 ValueError, logs 미완료 시 ValueError |
| `WorkflowData` | compositions/steps 유효 입력, 누락 필드 422 |
| `DeviceCommandRequest` | 허용 명령 OK, 허용 외 명령 422 |
| `BalanceCommand`, `FurnaceCommand` | Enum 값 직렬화/역직렬화 |

### 통합 테스트 대상

| 항목 | 테스트 케이스 |
|------|-------------|
| Rate Limiting | 로그인 6회 → 429, 1분 후 복구 |
| 강제 로그아웃 | force-logout 후 기존 JWT → 401 |
| Workflow 전이 | 순서 위반 전이 → 400, 정상 흐름 200 |
| ws_manager_client | MAX_RETRIES 초과 → task 종료 |
| 캐시 동시성 | 동시 update + read → 오류 없음 |

### E2E (Playwright) — 추후

- 로그인 brute force 후 잠금 해제 흐름
- 관리자 강제 로그아웃 → 연구원 자동 리다이렉트

---

## 6. Boundaries

### Never (절대 금지)

- `token_version` 검증 우회 경로 추가
- Rate Limit 기본값을 내부망이라는 이유로 제거
- 장치 명령에 `eval()` / 동적 실행 사용
- 로그에 비밀번호, JWT 원문 기록
- `asyncio.Lock` 보유 중 외부 I/O (SiLA2 gRPC) 호출

### Ask First (먼저 확인)

- uvicorn 워커 수 변경 (Rate Limit, Lock 정책 전체 재검토 필요)
- `token_version` 컬럼 이름/타입 변경 (마이그레이션 영향)
- Workflow 상태 한국어 값 변경 (DB 마이그레이션 + Enum 동시 수정)
- Phase 2 항목을 Phase 0/1과 묶어서 처리

### HTTPS 전환 플랜 (현 단계 보류)

현재: HTTP (내부망, 외부 접근 없음)

전환 트리거:
- 외부 접근 요구 발생
- 멀티 사이트 연구실 연동
- 게스트 Wi-Fi와 네트워크 분리 불확실

전환 방법:
1. nginx 또는 Caddy를 reverse proxy로 추가 (TLS 종단)
2. Electron 클라이언트 신뢰 인증서 배포
3. `ALLOWED_ORIGINS` 환경변수 업데이트
4. WebSocket `wss://` 프로토콜 전환

---

## 7. 진행 현황

| Phase | 항목 | 상태 |
|-------|------|------|
| 0-A | ws_manager_client 재시도 | 대기 |
| 0-B | DB 커넥션 풀 | 대기 |
| 0-C | Rate Limiting | 대기 |
| 1-A | 강제 로그아웃 (token_version) | 대기 |
| 1-B | 장치 명령 Enum | 대기 |
| 1-C | WS 예외 처리 | 대기 |
| 1-D | 로그 로테이션 | 대기 |
| 1-E | 캐시 동시성 | 대기 |
| 2-A | Workflow 상태 머신 | 대기 |
| 2-B | Workflow.data 스키마 | 대기 |
| 2-C | WS deadband | 대기 |
| 2-D | N+1 쿼리 개선 | 대기 |
