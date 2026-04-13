# LAB Pilot Demo

유리·세라믹 소재 연구를 위한 실험 워크플로우 자동화 플랫폼

> **Live Demo:** [https://inkyu0317.github.io/lab-pilot-demo/](https://inkyu0317.github.io/lab-pilot-demo/)

### 관련 프로젝트

| 레포지토리 | 설명 |
|-----------|------|
| [sila-server-manager](https://github.com/InKyu0317/sila-server-manager) | CB310 저울 등 실험 장비 SiLA 2 서버 모음 |
| [material-navigator-lib](https://github.com/InKyu0317/material-navigator-lib) | 유리 산화물 정적 데이터 Python 패키지 (mat_nav_lib) |

---

## 주요 기능

### 1. 모니터링 (Monitoring)
- SiLA2 기반 실험 장비 실시간 상태 모니터링
- 장비 관리자(Manager) → 서버(Server) 계층 구조 표시
- 장비별 온라인/오프라인 상태, 온도, 압력, 진행률 확인

### 2. 워크플로우 (Workflow)
**다중 조성(Multi-composition) 지원 탭 기반 워크플로우 편집기**

| 스텝 | 설명 |
|------|------|
| 조성 목록 | 워크플로우 내 여러 유리 조성을 AG Grid로 관리 (추가/편집/삭제) |
| 조성 설계 | 산화물 드롭다운 선택(70종), 배합비(wt%), 유리 종류 선택, 목표 물성 설정 (Tg, CTE, 밀도 등) |
| 칭량 (Weighing) | 조성별 배치 중량 및 원료 칭량 설정 |
| 혼합 (Mixing) | 혼합 시간, 메모 설정 |
| 성형 (Forming) | 형상(원형/바형) 및 치수 설정 |
| 소성 (Firing) | 다단 소성 프로파일 (승온율, 목표 온도, 유지 시간) 설정 |
| 열처리 (Heat Treatment) | 어닐링/템퍼링 온도, 시간, 냉각 방법 설정 |
| 가공 (Machining) | 가공 형상 및 정밀 치수 설정 |
| 분석 (Analysis) | 분석 항목별 측정값 입력 및 합격/불합격 판정 |

- **SiLA 장비 선택**: 모든 스텝에서 실험 장비를 지정 가능
- **AG Grid**: 조성 목록, 산화물 테이블, 물성 목표 테이블에 적용
- **localStorage 자동 저장**: 워크플로우 데이터 로컬 영구 보존

### 3. 실험 실행 (Experiment)
- 워크플로우 선택 후 단계별 실험 시뮬레이션 실행
- **실시간 차트** (vue-chartjs): 소성/열처리 온도 곡선 시각화
- 스텝별 진행 상태 타임라인 (대기/실행중/완료/실패)
- 실험 결과 요약 (조성, 칭량, 분석 결과)

### 4. 테마 시스템 (Theme)
**툴바 드롭다운으로 실시간 전환 가능한 9개 테마**

| 테마 | 설명 |
|------|------|
| 네이비 다크 | 전문적 · 신뢰감 |
| 차콜 그레이 | 모던 · 미니멀 |
| 미드나이트 그린 | 자연 · 안정감 |
| 슬레이트 블루 | 세련 · 차분 |
| 딥 오션 | 고급 · 대비 강함 |
| 웜 다크 | 따뜻함 · 편안함 |
| 노르딕 | 깔끔 · 북유럽 감성 |
| 사이버 테크 | 미래적 · 강렬 |
| 기본 라이트 | Quasar 기본 라이트 테마 |

- **폰트 변경**: Roboto, Inter, Pretendard, Noto Sans KR, IBM Plex Sans, JetBrains Mono
- **폰트 크기**: 12px ~ 18px 조절
- **AG Grid 테마 동기화**: 선택된 테마에 맞춰 AG Grid 색상 자동 변경
- **설정 영구 보존**: localStorage에 테마/폰트/크기 저장

---

## 기술 스택

### Frontend
| 카테고리 | 기술 |
|----------|------|
| Framework | Vue 3 (Composition API) + TypeScript 5.9 |
| UI | Quasar v2 (Vite) |
| 데이터 그리드 | AG Grid Community v35 |
| 차트 | vue-chartjs + Chart.js 4.x |
| 상태 관리 | Pinia v3 + Composables |
| 라우팅 | Vue Router v5 (hash mode) |
| 패키지 관리 | pnpm v10 |
| Node.js | v22+ |

### Backend
| 카테고리 | 기술 |
|----------|------|
| Framework | FastAPI 0.115+ |
| 서버 | uvicorn |
| 언어 | Python 3.10+ (conda `sila2_env`) |
| 장비 통신 | SiLA 2 (sila2==0.14.0) gRPC → WebSocket 브릿지 |
| 소재 데이터 | [mat_nav_lib](https://github.com/InKyu0317/material-navigator-lib) — 70종 산화물 정적 패키지 |

---

## 전체 프로젝트 구조

```
DEMO/
├── start-all.bat               # 전체 서버 시작 (Backend + Balance SiLA + Frontend)
├── stop-all.bat                # 전체 서버 중지
│
├── lab-pilot-demo/             # 본 레포지토리
│   ├── frontend/               # Vue 3 + Quasar 프론트엔드
│   │   └── src/
│   │       ├── layouts/
│   │       │   └── MainLayout.vue          # 사이드바 + 테마/폰트 툴바
│   │       ├── pages/
│   │       │   ├── MonitoringPage.vue       # SiLA 장비 모니터링
│   │       │   ├── WorkflowPage.vue         # 워크플로우 목록/편집
│   │       │   └── ExperimentPage.vue       # 실험 실행 시뮬레이션
│   │       ├── components/
│   │       │   └── workflow/
│   │       │       ├── types.ts             # 공용 타입 정의
│   │       │       ├── gridTheme.ts         # 반응형 AG Grid 테마
│   │       │       ├── WorkflowEditor.vue   # 탭 기반 워크플로우 편집기
│   │       │       ├── WorkflowList.vue     # AG Grid 워크플로우 목록
│   │       │       ├── DeviceSelector.vue   # SiLA 장비 선택
│   │       │       └── steps/              # 9개 스텝 컴포넌트
│   │       │           ├── CompositionListStep.vue
│   │       │           ├── CompositionStep.vue
│   │       │           ├── WeighingStep.vue
│   │       │           ├── MixingStep.vue
│   │       │           ├── FormingStep.vue
│   │       │           ├── FiringStep.vue
│   │       │           ├── HeatTreatStep.vue
│   │       │           ├── MachiningStep.vue
│   │       │           └── AnalysisStep.vue
│   │       └── composables/
│   │           ├── useTheme.ts              # 테마/폰트/크기 관리
│   │           ├── useWorkflows.ts          # 워크플로우 CRUD + localStorage
│   │           ├── useSilaDevices.ts        # SiLA 장비 목록 관리
│   │           ├── useMaterials.ts          # mat_nav_lib API 연동 (산화물 목록)
│   │           └── useExperimentRunner.ts   # 실험 시뮬레이션 엔진
│   └── backend/                # FastAPI 백엔드
│       └── app/
│           ├── main.py                     # FastAPI 진입점 + CORS
│           └── api/
│               ├── devices.py              # SiLA 장비 목록 API
│               ├── materials.py            # 산화물 목록 API (/api/materials/oxides)
│               └── ws.py                   # WebSocket SiLA 브릿지
│
├── ss_manager/                 # github.com/InKyu0317/sila-server-manager
│   └── balance/
│       ├── balance_server.py   # CB310 저울 SiLA 2 서버 (RS-232 :50051)
│       └── generated/          # WeightMeasurement SiLA Feature 코드
│
└── mat_nav_lib/                # github.com/InKyu0317/material-navigator-lib
    └── mat_nav_lib/
        ├── __init__.py         # get_oxides, get_oxide_formulas export
        └── oxides.py           # 70종 산화물 정적 데이터
```

### 포트 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Vue Frontend | :9002 | Quasar dev server |
| FastAPI Backend | :8000 | REST API + WebSocket |
| Balance SiLA | :50051 | CB310 저울 gRPC |

---

## 실행 방법

### 전체 서버 한 번에 시작 (권장)

`DEMO/` 루트의 배치 파일로 모든 서버를 시작/종료할 수 있습니다.

```
start-all.bat   # Backend + Balance SiLA + Frontend 동시 시작
stop-all.bat    # 전체 서버 종료
```

### 개별 실행

#### 사전 요구사항
- Node.js v22+, pnpm v10+
- Python 3.10+, conda 환경 `sila2_env`
- [mat_nav_lib](https://github.com/InKyu0317/material-navigator-lib) 설치 (`pip install -e ./mat_nav_lib`)

#### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

#### Backend

```bash
cd backend
# mat_nav_lib 경로를 PYTHONPATH에 추가
set PYTHONPATH=../../../mat_nav_lib   # Windows
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Balance SiLA Server

[sila-server-manager](https://github.com/InKyu0317/sila-server-manager) 레포 참조

```bash
cd ss_manager/balance
python balance_server.py --com COM11 --port 50051
```

### 프로덕션 빌드 (Frontend)

```bash
cd frontend
pnpm build
```

빌드 결과물은 `frontend/dist/spa/` 에 생성됩니다.

---

## 배포

GitHub Actions를 통해 `main` 브랜치 push 시 자동으로 GitHub Pages에 배포됩니다.

---

## 라이선스

MIT
