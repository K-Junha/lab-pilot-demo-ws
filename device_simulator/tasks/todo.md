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

## T4 — Rich TUI ✅

- [x] **4-A** `simulator/main.py` — balance/furnace 별 패널 렌더 함수 분리 (`_make_balance_panel`, `_make_furnace_panel`)
- [x] **4-B** Rich Live 루프 통합 — `while True: sleep(1)` 교체 (4회/초 갱신)
- [x] **4-C** Ctrl+C — `impl.stop()` + `server.stop()` 후 정상 종료 (server.stop 현재 누락)

## T5 — FurnaceClient (ss_manager) ✅

- [x] **5-A** `ss_manager/core/clients/furnace.py` 신규 — CurrentTemperature 구독, Setpoint 캐시
- [x] **5-B** `send_command("SetTemperature", {"target": ...})` → gRPC 호출 + 캐시 업데이트
- [x] **5-C** `ss_manager/core/tests/test_furnace_client.py` 신규 — _client_factory DI mock 테스트

## T6 — ss_manager lifespan furnace 지원 ✅

- [x] **6-A** `_clients` 타입 `dict[str, DeviceClient]`으로 확장 (콜 사이트 grep 후 타입 주석 변경)
- [x] **6-B** lifespan에 furnace 분기 추가 (fail-soft, 다중 장치 지원)
- [x] **6-C** `tests/test_main.py` — furnace 장치 lifespan 테스트 추가

## [Checkpoint C] — E2E 검증

- [ ] balance + furnace 시뮬레이터 동시 실행
- [ ] DevicesPage 스캔 → 두 장치 발견 → 등록
- [ ] ss_manager 재시작 → 두 장치 CONNECTED 확인
- [ ] Rich TUI 값 갱신 실시간 확인
- [ ] Ctrl+C → 포트 즉시 재사용 가능 확인
