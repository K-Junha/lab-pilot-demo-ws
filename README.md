# LAB Pilot Demo

유리·세라믹 소재 연구를 위한 실험 워크플로우 자동화 플랫폼

### 관련 프로젝트

| 레포지토리 | 설명 |
|-----------|------|
| [ss_manager](https://github.com/K-Junha/lab-pilot-demo-ws) | 실험실 계측 장비 관리 GUI 앱 (이 레포에 포함) |
| [material-navigator-lib](https://github.com/InKyu0317/material-navigator-lib) | 유리 산화물 정적 데이터 Python 패키지 |

---

## 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                        사용자 브라우저                            │
│                  http://localhost:9000                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP REST / WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              lab-pilot Backend  :8000                           │
│  FastAPI + SQLAlchemy + PostgreSQL + JWT                        │
│                                                                 │
│  /api/auth      — 회원가입 / 로그인 (JWT)                        │
│  /api/workflows — 워크플로우 CRUD (DB)                           │
│  /api/managers  — ss_manager 등록/조회 (DB)                     │
│  /ws/balance    — 저울 데이터 WebSocket 브릿지                    │
│  /ws/devices    — 장치 상태 WebSocket 스트림                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ WebSocket  ws://localhost:8765
                            │ (lab-pilot → ss_manager 연결)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              ss_manager  (Electron GUI 앱)                      │
│                                                                 │
│  Python Core                                                    │
│  ├─ REST API    :8766  — 장치 CRUD / 설정                        │
│  └─ WS Server   :8765  — lab-pilot 연결 수신 (frozen contract)   │
│                                                                 │
│  Electron + Vue/Quasar GUI                                      │
│  └─ 장치 관리 / 실시간 모니터 / 설정                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │ gRPC  :50051
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              balance_server.py  (SiLA2 gRPC 서버)               │
│  CB310 저울  RS-232 (COM·, 9600bps 7E1) → WeightMeasurement     │
└─────────────────────────────────────────────────────────────────┘
```

### 연결 흐름

1. **ss_manager** 실행 → `balance_server.py` 자동 시작 → WS 서버 :8765 열림
2. **lab-pilot Backend** 실행 → DB에 등록된 ss_manager에 WebSocket 연결 시도
3. ss_manager가 `auth_ok` 응답 → 장치 목록(UUID) 수신 → 0.5초 폴링으로 Weight 데이터 스트리밍
4. **lab-pilot Frontend** 로그인 → `/ws/balance`로 실시간 저울 데이터 수신

---

## 주요 기능

### 인증 (Auth)
- JWT Bearer 토큰 기반 인증
- 회원가입 / 로그인 / 내 정보 조회
- 관리자(admin) 권한: 사용자 관리, 전체 워크플로우 조회

### 워크플로우 (Workflow)
- 다중 조성(Multi-composition) 탭 기반 편집기
- 9단계 실험 스텝: 조성 설계 → 칭량 → 혼합 → 성형 → 소성 → 열처리 → 가공 → 분석
- 워크플로우 상태 흐름: **계획중 → 진행중 → 완료**
- 워크플로우 복사, 메모 작성
- DB 저장 (사용자별 격리)

### 실험 실행 (Experiment)
- 워크플로우 선택 후 단계별 진행
- Step 탭 잠금 (계획중 상태에서는 스텝 접근 불가)
- [실험 완료] 버튼으로 완료 처리

### 모니터링 (Monitoring)
- ss_manager에 등록된 장치의 실시간 상태 표시
- 저울: 실시간 중량 수치 + 물리 연결 상태 (CONNECTED / OFFLINE)

### 실험 로그 / 결과
- 실험 이벤트 로그 (필터 + 사이드패널)
- 완료된 실험 카드 → 상세 결과 조회

### 관리자 (Admin)
- 사용자 목록 관리 (생성/삭제/권한 변경)
- 전체 워크플로우 조회 (소유자 표시)
- ss_manager 등록 (host:port + API 키)

---

## 기술 스택

### Frontend
| 카테고리 | 기술 |
|----------|------|
| Framework | Vue 3 (Composition API) + TypeScript 5.9 |
| UI | Quasar v2 (Vite) |
| 데이터 그리드 | AG Grid Community v35 |
| 상태 관리 | Pinia v3 + Composables |
| 라우팅 | Vue Router v5 |
| 패키지 관리 | pnpm v10 |

### Backend
| 카테고리 | 기술 |
|----------|------|
| Framework | FastAPI 0.115+ (async) |
| ORM | SQLAlchemy 2.x async + asyncpg |
| DB | PostgreSQL |
| 마이그레이션 | Alembic |
| 인증 | JWT (python-jose) + bcrypt (passlib) |
| 설정 | pydantic-settings + .env |
| 장비 통신 | SiLA2 gRPC → WebSocket 브릿지 |

### ss_manager (장치 관리 GUI)
| 카테고리 | 기술 |
|----------|------|
| GUI | Electron + Vue 3 + Quasar v2 |
| 관리 API | FastAPI REST :8766 |
| 장치 브릿지 | WebSocket 서버 :8765 |
| 장치 통신 | SiLA2 gRPC (sila2 0.14.0) |
| 저장 | `~/.ss_manager/devices.json`, `settings.json` |

---

## 프로젝트 구조

```
lab-pilot-demo/
├── frontend/                     # Vue 3 + Quasar 프론트엔드
│   ├── src/
│   │   ├── css/app.css           # 디자인 토큰 (Dark Scientific 테마)
│   │   ├── layouts/
│   │   │   └── MainLayout.vue    # 사이드바 + 상단 툴바
│   │   ├── pages/
│   │   │   ├── LoginPage.vue
│   │   │   ├── MonitoringPage.vue
│   │   │   ├── WorkflowPage.vue
│   │   │   ├── ExperimentPage.vue
│   │   │   ├── LogPage.vue
│   │   │   ├── ResultsPage.vue
│   │   │   └── AdminPage.vue
│   │   ├── components/workflow/  # WorkflowEditor + 9개 스텝
│   │   └── composables/          # useAuth, useWorkflows, useSilaDevices ...
│   └── e2e/                      # Playwright e2e 테스트
│
├── backend/                      # FastAPI 백엔드
│   └── app/
│       ├── main.py               # FastAPI 진입점 + lifespan (ws_manager_client)
│       ├── models.py             # SQLAlchemy 모델
│       ├── database.py           # async DB 세션
│       └── api/
│           ├── auth.py           # /api/auth — 회원가입/로그인/me
│           ├── workflows.py      # /api/workflows — CRUD
│           ├── managers.py       # /api/managers — ss_manager 등록
│           ├── devices.py        # /api/devices — 장치 상태 조회
│           └── ws.py             # /ws/* — WebSocket 브릿지
│
└── ss_manager/                   # 장치 관리 GUI 앱 (별도 실행)
    ├── core/                     # Python FastAPI 백엔드
    │   ├── main.py               # REST :8766 + WS 서버 시작
    │   ├── ws_server.py          # WS :8765 — lab-pilot 연결 수신
    │   ├── device_registry.py    # 장치 CRUD (devices.json)
    │   ├── clients/
    │   │   ├── balance.py        # CB310 gRPC 클라이언트
    │   │   └── base.py           # DeviceClient ABC
    │   └── balance/              # balance_server.py (SiLA2 gRPC 서버)
    └── gui/                      # Electron + Vue/Quasar
        ├── src-electron/         # electron-main.ts (Python spawn + tray)
        └── src/
            ├── layouts/MainLayout.vue
            └── pages/
                ├── DevicesPage.vue   # 장치 관리
                ├── MonitorPage.vue   # 실시간 모니터
                └── SettingsPage.vue  # 설정
```

### 포트 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Frontend (dev) | :9000 | Quasar dev server |
| Backend | :8000 | FastAPI REST + WebSocket |
| ss_manager REST | :8766 | GUI 관리 API |
| ss_manager WS | :8765 | lab-pilot 연결 수신 |
| Balance gRPC | :50051 | CB310 저울 SiLA2 서버 |

---

## 실행 방법

### 사전 요구사항

- Node.js v22+, pnpm v10+
- Python 3.11, conda 환경 `sila2_env`
- PostgreSQL 실행 중
- `mat_nav_lib` 설치: `pip install -e ./mat_nav_lib`

### 1. ss_manager 실행 (장치 관리 GUI)

```bash
cd ss_manager/gui
pnpm install
pnpm electron:dev
```

> GUI 앱이 열리면서 Python 서버가 자동 시작됩니다.
> 장치 탭에서 CB310 저울을 추가하세요 (COM3, gRPC 50051).

Python만 단독 실행하려면:

```bash
cd ss_manager
conda activate sila2_env
python -m core.main --port 8766 --ws-port 8765
```

### 2. lab-pilot Backend 실행

```bash
cd backend
conda activate sila2_env
# 최초 1회: DB 마이그레이션
alembic upgrade head
# 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. lab-pilot Frontend 실행

```bash
cd frontend
pnpm install
pnpm dev
# → http://localhost:9000
```

### 4. ss_manager 등록 (최초 1회)

1. 브라우저에서 `http://localhost:9000` 접속 → 회원가입 → 로그인
2. 관리자 계정으로 **Admin → SS Manager 탭** 이동
3. [새 Manager 추가]: host `127.0.0.1`, port `8765`, API 키 `local-dev-key`
4. Backend 재시작 → 콘솔에 `연결 성공: manager_id=1` 확인

---

## 테스트

```bash
# e2e (Playwright) — 백엔드 불필요, API mock
cd frontend
pnpm test:e2e
# → 24 passed, 1 skipped
```

---

## 라이선스

MIT
