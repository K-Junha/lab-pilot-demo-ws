# device_simulator — Task List

> 상세 내용: tasks/plan.md

## T1 — Balance 시뮬레이터 코어

- [ ] **1-A** `pyproject.toml` + 패키지 구조 초기화
- [ ] **1-B** `ss_manager/core/balance/generated/` → `simulator/devices/generated/` 복사
- [ ] **1-C** `devices/balance.py` — BalanceSimImpl (WeightMeasurementBase 구현, 노이즈 모델)
- [ ] **1-D** `simulator/main.py` 최소 구현 (argparse + SilaServer + push thread, TUI 없음)
- [ ] **1-E** `ss_manager/core/main.py` lifespan 분기 (com 없으면 subprocess 미실행)

**[Checkpoint A]** ss_manager BalanceClient → 시뮬레이터 구독 → lab-pilot 무게값 표시

## T2 — mDNS + /api/scan + DevicesPage UI

- [ ] **2-A** `simulator/mdns.py` — zeroconf ServiceInfo 등록/해제
- [ ] **2-B** `ss_manager/core/scan.py` — COM 포트 스캔 + mDNS ServiceBrowser
- [ ] **2-C** `ss_manager/core/main.py` — `GET /scan` 엔드포인트 추가
- [ ] **2-D** `ss_manager/core/pyproject.toml` — zeroconf 의존성 추가
- [ ] **2-E** `ss_manager/gui/src/pages/DevicesPage.vue` — 스캔 버튼 + 드롭다운 UI

**[Checkpoint B]** 시뮬레이터 실행 → DevicesPage 스캔 → 발견 → 등록 → 무게값 수신

## T3 — Furnace 시뮬레이터

- [ ] **3-A** ⚠️ 스파이크: sila2.code_generator로 TemperatureController.sila.xml 생성 검증
- [ ] **3-B** `devices/furnace.py` — FurnaceSimImpl (1차 지연계 열 모델)
- [ ] **3-C** `simulator/main.py` — furnace 분기 추가
- [ ] **3-D** `DevicesPage.vue` — furnace 타입 항목 표시

## T4 — Rich TUI

- [ ] **4-A** `simulator/main.py` — Rich Live 통합 (값 실시간 표시)
- [ ] **4-B** Ctrl+C 처리 — mDNS unregister 후 정상 종료
