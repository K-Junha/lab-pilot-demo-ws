# LAB PILOT — 프로젝트 규칙

> 전역 규칙(`~/.claude/CLAUDE.md`)에 추가되는 프로젝트별 규칙

---

## 기술 스택

- **Frontend**: Vue 3 + TypeScript 5.9+ + Quasar v2 + AG Grid v35 + Pinia
- **Backend**: FastAPI (async) + SQLAlchemy async + asyncpg + Alembic
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **설정**: pydantic-settings + .env
- **e2e**: Playwright CLI (`pnpm test:e2e`)

## 코드 규칙

### Frontend

- `<script setup lang="ts">` 형태 통일
- `any` 타입 금지 — 명시적 타입 사용
- SCSS 주석: `/* */` 사용 (`//` 금지 — sass-embedded 크래시)
- API 호출 함수는 `.data` unwrap 반환
- 전역 상태만 Pinia, 나머지는 composables
- 테마: `useTheme.ts` 기존 9개 고정 (수정 금지)

### Backend

- 모든 핸들러 `async def`
- async 핸들러 내 blocking IO → `asyncio.to_thread()`
- DB 세션: `Depends(get_db)` 패턴
- 인증: `Depends(get_current_user)` (JWT Bearer)
- 로깅: 모든 주요 작업 `get_logger(TYPE).info/warning/error()`
- 환경변수: `.env` + pydantic-settings

## 절대 금지

- `SECRET_KEY` 기본값 하드코딩
- WebSocket JWT를 URL 쿼리 파라미터로 전달
- SCSS `//` 주석
- CORS `allow_origins=["*"]` 운영 환경 사용
- 로그에 비밀번호·토큰 값 기록
- `any` 타입 (TypeScript)

## 먼저 확인 필요

- DB 스키마 변경 (Alembic 마이그레이션 영향)
- 기존 composables 인터페이스 변경
- 새 외부 패키지 추가

## worklog

전역 규칙(`~/.claude/CLAUDE.md`)에 따라 `worklog/worklog_YYYY-MM-DD.md`에 기록
