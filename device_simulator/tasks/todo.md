# device_simulator — Task List

> 상세 내용: tasks/plan.md

## T1 — Balance 시뮬레이터 코어 ✅

- [x] **1-A** `pyproject.toml` + 패키지 구조 초기화
- [x] **1-B** `ss_manager/core/balance/generated/` → `simulator/devices/generated/` 복사
- [x] **1-C** `devices/balance.py` — BalanceSimImpl (WeightMeasurementBase 구현, 노이즈 모델)
- [x] **1-D** `simulator/main.py` 최소 구현 (argparse + SilaServer + push thread, TUI 없음)
- [x] **1-E** `ss_manager/core/main.py` lifespan 분기 (com 없으면 subprocess 미실행)

**[Checkpoint A]** ✅ SiLA2 클라이언트로 Weight 5회 수신 확인
> 발견: SiLA2 프레임워크가 zeroconf를 내장 — T2 mdns.py 별도 구현 불필요

## T2 — mDNS + /api/scan + DevicesPage UI ✅

- [x] **2-A** `simulator/mdns.py` — SiLA2 내장 zeroconf 사용으로 별도 구현 불필요
- [x] **2-B** `ss_manager/core/scan.py` — COM 포트 스캔 + mDNS ServiceBrowser (`_sila._tcp.local.`)
- [x] **2-C** `ss_manager/core/main.py` — `GET /scan` 엔드포인트 추가 (`asyncio.to_thread`)
- [x] **2-D** `ss_manager/core/pyproject.toml` — `zeroconf>=0.115` 의존성 추가
- [x] **2-E** `ss_manager/gui/src/pages/DevicesPage.vue` — 스캔 버튼 + 스캔 결과 다이얼로그 UI

**[Checkpoint B]** 시뮬레이터 실행 → DevicesPage 스캔 → 발견 → 등록 → 무게값 수신

## T3 — Furnace 시뮬레이터 ✅

- [x] **3-A** ⚠️ 스파이크: sila2.code_generator로 TemperatureController.sila.xml 생성 검증 — 성공 (sila2[codegen] 설치 필요)
- [x] **3-B** `devices/furnace.py` — FurnaceSimImpl (1차 지연계 열 모델, tau=30s)
- [x] **3-C** `simulator/main.py` — furnace 분기 추가
- [x] **3-D** `DevicesPage.vue` — furnace 타입 항목 표시 + balance 시뮬레이터 모드 지원

## T4 — Rich TUI

- [ ] **4-A** `simulator/main.py` — Rich Live 통합 (값 실시간 표시)
- [ ] **4-B** Ctrl+C 처리 — mDNS unregister 후 정상 종료
