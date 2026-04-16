# LAB PILOT — Progress

> 최종 업데이트: 2026-04-16

---

## 현재 단계: Phase 4 완료 · Phase 5 완료 — 다음 작업 대기

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
- **미커밋**: Phase 5 + Phase 4 (/review, /ship, e2e) 전체 — 커밋 대기 중

---

## Out of Scope (추후 / 타 담당자)

- F05 샘플 가져오기
- F06 QR코드 PDF 출력
- F10 사진 업로드/갤러리
- F20 바코드 없이 시작
- AI 분석 (GlassNet+BO) — mat_nav_lib 담당자
- SSMANAGER 분산 구조 — Phase D
- SiLA 전기로·Step 3~8 연동 — 하드웨어 미준비
