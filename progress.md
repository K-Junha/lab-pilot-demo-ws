# LAB PILOT — Progress

> 최종 업데이트: 2026-04-23

---

## 현재 단계: device_simulator SPEC 완료 — plan 대기 중

### device_simulator — 가상 장치 시뮬레이터 (2026-04-23)

| 항목 | 상태 | 날짜 |
|------|------|------|
| VIRTUAL_SIMULATION_PLAN.md 검토 및 방향 재정립 | ✅ 완료 | 2026-04-23 |
| device_simulator/SPEC.md 작성 | ✅ 완료 | 2026-04-23 |
| tasks/plan.md 작성 | ⬜ 대기 | — |
| 구현 | ⬜ 대기 | — |

---

## 이전 단계: Phase 7 완료 — pnpm lint 0 errors, 빌드 성공

### Phase 7 — 코드 품질 & 로깅 규칙화 (2026-04-22 완료)

| 항목 | 상태 | 날짜 |
|------|------|------|
| tasks/plan.md Phase 7 섹션 추가 | ✅ 완료 | 2026-04-22 |
| tasks/todo.md Phase 7 항목 추가 | ✅ 완료 | 2026-04-22 |
| T7.1 logging-rules.md + .env 보완 | ✅ 완료 | 2026-04-22 |
| T7.2 Lint 안전 수정 (98→47 errors) | ✅ 완료 | 2026-04-22 |
| T7.3 Lint vue/no-mutating-props → 0 errors (defineModel) | ✅ 완료 | 2026-04-22 |
| T7.4 백엔드 로그 타입 정렬 + purge_old_logs() | ✅ 완료 | 2026-04-22 |
| T7.5 한국어 주석 (프론트엔드) | ✅ 완료 | 2026-04-22 |
| T7.6 한국어 주석 (백엔드) | ✅ 완료 | 2026-04-22 |

---

## 현재 단계 이전: 전체 완료 — lab-pilot Phase 1~6 + ss_manager GUI 앱 커밋 완료

### ss_manager GUI App (신규 — 2026-04-21~)

| 항목 | 상태 | 날짜 |
|------|------|------|
| SPEC.md 작성 (6개 영역) | ✅ 완료 | 2026-04-21 |
| tasks/plan.md + todo.md 작성 (9개 태스크) | ✅ 완료 | 2026-04-21 |
| Task 1 — 프로젝트 구조 초기화 | ✅ 완료 | 2026-04-21 |
| Task 2 — device_registry.py | ✅ 완료 | 2026-04-21 |
| Task 3 — clients/base.py + generic.py | ✅ 완료 | 2026-04-21 |
| Task 4 — clients/balance.py | ✅ 완료 | 2026-04-21 |
| Task 5 — ws_server.py | ✅ 완료 | 2026-04-21 |
| Task 6 — core/main.py (FastAPI) | ✅ 완료 | 2026-04-21 |
| Task 7 — Electron shell | ✅ 완료 | 2026-04-21 |
| Task 8 — Vue/Quasar UI | ✅ 완료 | 2026-04-21 |
| Task 9 — 테스트 + 통합 검증 | ✅ 완료 | 2026-04-21 |
| /test — pytest 31 passed + e2e 24 passed | ✅ 완료 | 2026-04-21 |
| /review — Important 4건 + Suggestion 4건 식별 | ✅ 완료 | 2026-04-21 |
| /review Fix 적용 (I-1~I-4) | ✅ 완료 | 2026-04-22 |

#### /review Fix 목록 (내일 작업)

| Fix | 파일 | 내용 |
|-----|------|------|
| I-1 | `gui/src/pages/SettingsPage.vue:71` | 개인 경로 하드코딩 제거 |
| I-2 | `core/clients/balance.py:57-59` | `stop()` thread join 추가 |
| I-3 | `gui/src/pages/DevicesPage.vue:209,225` | submitAdd/doDelete 실패 Quasar notify 추가 |
| I-4 | `DevicesPage.vue:187`, `MonitorPage.vue:107` | unmount 후 WS 재연결 방지 (`destroyed` 플래그) |

---

## Phase 4 완료 · Phase 5 완료 — lab-pilot UI 리디자인

### 플랜 산출물 ✅

| 항목 | 상태 | 날짜 |
|------|------|------|
| tasks/plan.md 작성 (Task별 수락 기준 포함) | ✅ 완료 | 2026-04-14 |
| tasks/todo.md 작성 (체크박스 진행 추적) | ✅ 완료 | 2026-04-14 |
| tasks/plan.md 보완 (WEB 이식 패턴 반영) | ✅ 완료 | 2026-04-15 |
| doc/web-optimization-insights.md (WEB 프로젝트 개선사항 분석) | ✅ 완료 | 2026-04-16 |
| tasks/review-plan.md (Fix 1~4 + S1 수정 계획) | ✅ 완료 | 2026-04-16 |

### Phase 0 — 설계 ✅

| 항목 | 상태 | 날짜 |
|------|------|------|
| WEB(9차) + bkit_test 분석 문서 작성 | ✅ 완료 | 2026-04-14 |
| 3개 GitHub 리포 클론 (lab-pilot-demo / ss_manager / mat_nav_lib) | ✅ 완료 | 2026-04-14 |
| lab-pilot-demo 소스 분석 (기존 기능 파악) | ✅ 완료 | 2026-04-14 |
| SPEC.md 작성 | ✅ 완료 | 2026-04-14 |

### Phase 1 — 인증·DB 기반 ✅

| ID | 항목 | 상태 |
|----|------|------|
| L1-5 | config.py + .env (SECRET_KEY 강제화) | ✅ |
| L1-3 | database.py + models.py | ✅ |
| L1-6 | Alembic 초기 마이그레이션 | ✅ |
| L1-3 | dependencies.py (get_db, get_current_user, require_admin) | ✅ |
| L1-1 | auth.py API (register / login) + /me | ✅ |
| L1-2 | useAuth.ts + LoginPage.vue + 라우터 가드 | ✅ |
| L1-4 | workflows.py API (localStorage → DB CRUD) | ✅ |
| L1-4 | useWorkflows.ts DB API 연동 교체 | ✅ |

### Phase 2 — 보안 강화 ✅

| ID | 항목 | 상태 |
|----|------|------|
| F13 | WebSocket JWT 첫 메시지 인증 | ✅ |
| F14 | CORS 환경변수 분리 | ✅ |
| F17 | LpLogger + logging_middleware.py | ✅ |

### Phase 3 — 기능 이식 ✅

| ID | 항목 | 상태 |
|----|------|------|
| F02 | Plan 상태 흐름 (계획중→진행중→완료) | ✅ |
| F03 | Step 탭 잠금 (계획중 비활성) | ✅ |
| F04 | [실험 완료] 버튼 | ✅ |
| F01 | Plan 복사 다이얼로그 | ✅ |
| F07 | Log 페이지 (필터 + 사이드패널) | ✅ |
| F08 | data_collected 요약 컬럼 | ✅ |
| F09 | Results 페이지 (완료 실험 카드 → 상세) | ✅ |
| F11 | 노트 작성 (Plan, 완료 실험) | ✅ |
| F12 | 장치 자동시작 lifespan + 워치독 | ✅ |
| F15 | Admin 사용자 관리 | ✅ |
| F16 | Admin 전체 워크플로우 소유자 표시 | ✅ |

### Phase 4 — 검증 ✅

| 항목 | 상태 | 비고 |
|------|------|------|
| Playwright e2e 확장 및 통과 | ✅ | 24 passed, 1 skipped |
| /review 코드 리뷰 | ✅ | Important 4건 + S1 수정 완료 |
| /ship 배포 체크리스트 | ✅ | audit 0건, build 성공 |

#### Phase 4 상세 — /review Fix 목록

| Fix | 내용 | 파일 |
|-----|------|------|
| Fix 1 | 미사용 `datetime` import 제거 | `devices.py` |
| Fix 2 | `get_event_loop()` → `get_running_loop()` | `manager.py` (3곳) |
| Fix 3 | 미사용 `_ws_executor` 제거 | `ws.py`, `main.py` |
| Fix 4 | send_command → command_queue 방식 | `ws_manager_client.py` |
| Fix S1 | stop_all() gather 대기 추가 | `ws_manager_client.py` |

#### Phase 4 상세 — /ship lint 수정

| 파일 | 수정 내용 |
|------|-----------|
| `AdminPage.vue` | `no-misused-promises` — `_execDeleteManager`, `_execDeleteUser` 헬퍼 분리 |
| `MonitoringPage.vue` | `no-misused-promises` — setInterval 내 `void` 패턴 적용 |
| `.env.example` | `MANAGER_API_KEY` 항목 누락 추가 |

#### Phase 4 상세 — e2e 구조

| 파일 | 테스트 수 | 내용 |
|------|-----------|------|
| `e2e/helpers/auth.ts` | — | `injectAuth` (addInitScript), API mock 헬퍼 |
| `e2e/auth.spec.ts` | 6 | 로그인/회원가입/리다이렉트/로그아웃 |
| `e2e/navigation.spec.ts` | 5 | 페이지 이동 + 인증 가드 |
| `e2e/workflow.spec.ts` | 9 | 워크플로우 CRUD + 에디터 |
| `e2e/experiment.spec.ts` | 5 | 실험 페이지 + 모니터링 |

### Phase 5 — Architecture B (ss_manager ↔ WebSocket pull) ✅

| ID | 항목 | 상태 |
|----|------|------|
| 5.1 | SsManager DB 모델 + Admin CRUD API | ✅ |
| 5.2 | ws_manager_client.py 신규 + main.py lifespan | ✅ |
| 5.3 | /api/managers REST + ws.py 캐시 기반 전환 | ✅ |
| 5.4 | ss_manager/manager.py 신규 (WS 서버 + gRPC 클라이언트) | ✅ |
| 5.5 | AdminPage.vue ss_manager 탭 + useSilaDevices.ts mock 제거 | ✅ |

---

## 로컬 실행 환경 (2026-04-14 기준)

| 항목 | 내용 |
|------|------|
| conda 환경 | `sila2_env` (Python 3.11) |
| 백엔드 실행 | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` |
| 프론트엔드 실행 | `cd frontend && pnpm dev` → http://localhost:9000 |
| e2e 테스트 | `cd frontend && pnpm test:e2e` (백엔드 불필요 — API mock) |
| DB | PostgreSQL (alembic upgrade head 완료, 0002_add_ss_managers 포함) |
| mat_nav_lib | `pip install -e ../../mat_nav_lib` 별도 설치 필요 |
| bcrypt | `pip install "bcrypt>=3.2.0,<4.1.0"` 버전 고정 필요 |

## 버그픽스 이력 (2026-04-22 추가)

| 항목 | 해결 방법 |
|------|-----------|
| IP 접근 시 CORS 차단 | `.env` `ALLOWED_ORIGINS`에 `192.168.1.103:9000~9002` 추가 |
| 프론트엔드 API URL 하드코딩 | `frontend/.env` + `VITE_API_BASE_URL` / `VITE_WS_BASE_URL` 환경변수 도입, 9개 파일 교체 |
| Quasar 포트 미명시 | `quasar.config.ts` devServer `port: 9000` 추가 |
| `config.py` CORS 기본값 9002만 허용 | 9000~9002, 5173 포함으로 수정 |
| `start-all.bat` 포트 주석 오기 | `:9002` → `:9000` 수정 |

## 버그픽스 이력 (2026-04-14)

| 항목 | 해결 방법 |
|------|-----------|
| conda env 없음 | `conda create -n sila2_env python=3.11 -y` |
| setuptools 패키지 충돌 | pyproject.toml에 `[tool.setuptools.packages.find] include = ["app*"]` |
| alembic CP949 인코딩 오류 | alembic.ini 한국어 주석 제거 |
| asyncpg WinError 64 | alembic env.py → psycopg2 동기 방식으로 전환 |
| psycopg2 bcrypt 비호환 | `bcrypt<4.1.0` 고정, 비밀번호 72바이트 상한 validator 추가 |
| AG Grid cellRenderer TypeError | `h()` VNode → `document.createElement()` DOM 엘리먼트로 교체 |
| CORS OPTIONS 400 | ALLOWED_ORIGINS에 9000~9002, 5173 포트 추가 |
| QPage 레이아웃 오류 | LoginPage `q-page` → `div` 교체 (독립 라우트는 QLayout 없음) |

## Git 상태

- **Fork**: https://github.com/K-Junha/lab-pilot-demo-ws
- **Upstream**: https://github.com/InKyu0317/lab-pilot-demo
- **lab-pilot-demo 커밋**: `9368502` feat: Phase 6 UI redesign + ws.py UUID fix + README (2026-04-22)
- **ss_manager 커밋**: `ea78663` feat: GUI app — Electron + Vue/Quasar + Python FastAPI (2026-04-22)
- **Phase 7 완료**: `pnpm lint` 0 errors, `pnpm build` 성공 (2026-04-22)

---

## Phase 6 — UI Redesign (진행 예정)

| 항목 | 상태 | 비고 |
|------|------|------|
| SPEC-ui-redesign.md 작성 | ✅ 완료 | 2026-04-20 |
| Foundation (app.css + dark mode + 폰트) | ✅ 완료 | 2026-04-21 |
| MainLayout 재설계 | ✅ 완료 | 2026-04-21 |
| 7개 페이지 템플릿 재설계 | ✅ 완료 | 2026-04-21 |
| WorkflowList AG Grid → 그룹 리스트 교체 | ✅ 완료 | 2026-04-21 |
| pnpm build + e2e 검증 | ✅ 완료 | 2026-04-22 |

> 기반: Claude Design 결과물 `LAB Pilot v2.html` (Dark Scientific Instrument 테마)
> 범위: 프론트엔드 시각 레이어만 — 스크립트·백엔드·e2e 무변경

---

## Out of Scope (추후 / 타 담당자)

- F05 샘플 가져오기
- F06 QR코드 PDF 출력
- F10 사진 업로드/갤러리
- F20 바코드 없이 시작
- AI 분석 (GlassNet+BO) — mat_nav_lib 담당자
- SSMANAGER 분산 구조 — Phase D
- SiLA 전기로·Step 3~8 연동 — 하드웨어 미준비
