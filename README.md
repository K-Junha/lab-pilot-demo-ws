# LAB Pilot Demo

유리 소재 연구를 위한 AI 기반 실험 워크플로우 관리 플랫폼

> **Live Demo:** [https://inkyu0317.github.io/lab-pilot-demo/](https://inkyu0317.github.io/lab-pilot-demo/)

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
| 조성 설계 | 산화물 배합비(wt%), 유리 종류 선택, 목표 물성 설정 (Tg, CTE, 밀도 등) |
| 칭량 (Weighing) | 조성별 배치 중량 및 원료 칭량 설정 |
| 용융 (Melting) | 용융 온도, 시간, 분위기 조건 설정 |
| 소성 (Firing) | 소성 프로파일 (온도, 시간, 승온율) 설정 |
| 열처리 (Heat Treatment) | 어닐링/템퍼링 조건 설정 |
| 분석 (Analysis) | 분석 항목 및 방법 설정 |

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

---

## 프로젝트 구조

```
src/
├── layouts/
│   └── MainLayout.vue          # 메인 레이아웃 (사이드바 + 테마/폰트 툴바)
├── pages/
│   ├── MonitoringPage.vue       # SiLA 장비 모니터링
│   ├── WorkflowPage.vue         # 워크플로우 목록/편집
│   └── ExperimentPage.vue       # 실험 실행 시뮬레이션
├── components/
│   └── workflow/
│       ├── types.ts             # 공용 타입 정의
│       ├── gridTheme.ts         # 반응형 AG Grid 테마
│       ├── WorkflowEditor.vue   # 탭 기반 워크플로우 편집기
│       ├── WorkflowList.vue     # AG Grid 워크플로우 목록
│       ├── DeviceSelector.vue   # SiLA 장비 선택 컴포넌트
│       └── steps/               # 7개 스텝 컴포넌트
│           ├── CompositionListStep.vue
│           ├── CompositionStep.vue
│           ├── WeighingStep.vue
│           ├── MeltingStep.vue
│           ├── FiringStep.vue
│           ├── HeatTreatmentStep.vue
│           └── AnalysisStep.vue
├── composables/
│   ├── useTheme.ts              # 테마/폰트/크기 관리
│   ├── useWorkflows.ts          # 워크플로우 CRUD + localStorage
│   ├── useSilaDevices.ts        # SiLA 장비 목록 관리
│   └── useExperimentRunner.ts   # 실험 시뮬레이션 엔진
└── router/
    └── routes.ts                # 라우트 정의
```

---

## 실행 방법

### 사전 요구사항
- Node.js v22+
- pnpm v10+

### 설치 및 실행

```bash
pnpm install
pnpm dev
```

### 프로덕션 빌드

```bash
pnpm build
```

빌드 결과물은 `dist/spa/` 에 생성됩니다.

---

## 배포

GitHub Actions를 통해 `main` 브랜치 push 시 자동으로 GitHub Pages에 배포됩니다.

---

## 라이선스

MIT
