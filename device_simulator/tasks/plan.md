# device_simulator — 구현 계획

> SPEC: `device_simulator/SPEC.md`
> 작성일: 2026-04-24

---

## 아키텍처 결정 요약

| 결정 | 선택 | 이유 |
|------|------|------|
| Balance XML 공유 방식 | generated/ 디렉터리 복사 | ss_manager 직접 import 금지 (SPEC Boundaries) |
| com-less config 분기 | `"com" not in cfg.config` | 키 부재로 판별 — null보다 명확 |
| mDNS 서비스 타입 | `_sila._tcp.local.` | SiLA2 표준 준수, TXT records로 타입 필터링 |
| scan.py async 방식 | sync ServiceBrowser + run_in_executor | AsyncZeroconf 대비 단순 |
| Furnace 접근 | sila2.code_generator 스파이크 우선 | 생성 실패 시 수동 스텁 fallback |
| TUI 스레드 | Rich Live 메인, sila2·mDNS bg thread | 각 컴포넌트 독립 |
| Furnace ss_manager 연결 | 범위 외 (표시만) | Part 2는 balance에 집중 |

---

## 작업 순서 (수직 슬라이싱)

```
T1: Balance 시뮬레이터 코어
    ↓ [Checkpoint A]
T2: mDNS + /api/scan + DevicesPage UI
    ↓ [Checkpoint B]
T3: Furnace 시뮬레이터
    ↓
T4: Rich TUI
```

---

## T1 — Balance 시뮬레이터 코어

**목표**: ss_manager BalanceClient가 시뮬레이터에 구독하여 무게 데이터를 수신한다.

### 작업 내용

**1-A. 프로젝트 초기화**
- `device_simulator/pyproject.toml` 작성
  ```toml
  [project]
  name = "device-simulator"
  version = "0.1.0"
  requires-python = ">=3.11"
  dependencies = [
      "sila2==0.14.0",
      "zeroconf>=0.115",
      "rich>=13",
      "pyserial>=3.5",
  ]
  ```
- `simulator/__init__.py`, `simulator/devices/__init__.py` 생성

**1-B. WeightMeasurement generated/ 복사**
- `ss_manager/core/balance/generated/` → `device_simulator/simulator/devices/generated/` 복사
  - `weightmeasurement_base.py`
  - `weightmeasurement_feature.py`
  - `weightmeasurement_types.py`
  - `WeightMeasurement.sila.xml`
  - `__init__.py`
- 주석: `# ss_manager/core/balance/generated/ 와 동일 버전 유지 필요`

**1-C. `devices/balance.py` 구현**
```python
class BalanceSimImpl(WeightMeasurementBase):
    # 시뮬레이션 상태
    _base_weight: float = 0.0  # SetZero 기준값
    _offset: float = 0.0       # 랜덤워크 누적값

    def _push_loop(self):
        # 50ms 간격, 랜덤워크 노이즈
        # weight = _offset + gaussian(0, 0.002 * max(abs(_offset), 1.0))
        # update_Weight(weight)

    def SetZero(self, *, metadata) -> SetZero_Responses:
        # _offset = 0.0 (현재 기준점을 0으로)
```

**1-D. `simulator/main.py` 최소 구현 (TUI 없음)**
```python
# argparse: --device, --port, --name, --host
# SilaServer 생성 + BalanceSimImpl 연결
# server.start_insecure(host, port)  # non-blocking
# push_thread.start()  # daemon
# while True: time.sleep(1)  # 메인 유지
```

**1-E. ss_manager `main.py` lifespan 수정**
```python
# 변경 전
_balance_proc = await _start_balance_subprocess(...)
await asyncio.sleep(2)
client = BalanceClient(...)

# 변경 후
if cfg.config.get("com"):
    _balance_proc = await _start_balance_subprocess(...)
    await asyncio.sleep(2)
# com 없으면 subprocess 없이 직접 연결
client = BalanceClient(cfg.id, cfg.name, cfg.config)
await client.start()
```

### 수락 기준
- `python -m simulator --device balance --port 50051` 실행 후 프로세스가 종료되지 않음
- ss_manager 시작 시 balance 장치가 `{grpc_host: "127.0.0.1", grpc_port: 50051}` config로 등록되어 있으면 subprocess 없이 BalanceClient 연결 성공
- lab-pilot WeighingRunner에 실시간 무게값이 표시됨 (노이즈 포함)
- SetZero 명령 후 표시값이 0 근처로 리셋됨
- Ctrl+C 시 시뮬레이터 정상 종료

### 검증
```bash
# 터미널 1: 시뮬레이터 실행
cd device_simulator && pip install -e .
python -m simulator --device balance --port 50051

# 터미널 2: ss_manager (balance 장치 미리 등록: grpc_host, grpc_port 50051, com 없음)
cd ss_manager/gui && pnpm electron:dev
# DevicesPage에서 balance 장치 수동 추가 (com 필드 비움)

# 터미널 3: lab-pilot WeighingRunner에서 무게값 확인
```

---

## [Checkpoint A]

- [ ] `python -m simulator --device balance` 실행 성공
- [ ] ss_manager BalanceClient 연결 성공 (로그: `[balance] gRPC 구독 시작`)
- [ ] lab-pilot WeighingRunner 무게값 수신 확인
- [ ] Ctrl+C 정상 종료

---

## T2 — mDNS + /api/scan + DevicesPage UI

**목표**: 시뮬레이터를 실행하면 ss_manager DevicesPage에서 스캔으로 발견하고 등록할 수 있다.

### 작업 내용

**2-A. `simulator/mdns.py` 구현**
```python
from zeroconf import Zeroconf, ServiceInfo

class SimulatorMdns:
    def register(self, name, device_type, host, port): ...
    def unregister(self): ...

# TXT records: {"device_type": "balance", "sila_version": "2.0", "simulator": "true"}
# 서비스 타입: "_sila._tcp.local."
# 등록 시점: SilaServer start_insecure 호출 후 1s 대기
```

**2-B. ss_manager `core/scan.py` 신규**
```python
import asyncio
from serial.tools.list_ports import comports
from zeroconf import Zeroconf, ServiceBrowser, ServiceListener

_cache: dict | None = None
_cache_time: float = 0
CACHE_TTL = 30.0

def scan_com_ports() -> list[dict]:
    # comports() 결과, port/description/hwid 포함

async def scan_sila_services(timeout: float = 2.0) -> list[dict]:
    # asyncio.get_event_loop().run_in_executor(None, _sync_scan, timeout)
    # ServiceBrowser → 2s 후 결과 반환

async def scan_all(force: bool = False) -> dict:
    # cache 확인 → 만료 시 재스캔
    # {"com_ports": [...], "sila_services": [...]}
```

**2-C. ss_manager `main.py` `/api/scan` 엔드포인트 추가**
```python
@app.get("/scan")
async def get_scan(force: bool = False):
    return await scan_all(force=force)
```

**2-D. ss_manager `core/pyproject.toml` 의존성 추가**
```toml
"zeroconf>=0.115",
```

**2-E. DevicesPage.vue 스캔 UI 추가**
```
장치 추가 다이얼로그:

[스캔] 버튼 (로딩 스피너 포함)
─────────────────────────────
● COM3 — USB Serial Port (FTDI...)    ← 선택 시 type=balance, com=COM3 자동입력
◈ Sim-Balance-01 :50051 [SIM]         ← 선택 시 type=balance, grpc_host/port 자동입력
발견된 장치 없음 (스캔 결과 없을 때)
─────────────────────────────
수동 입력 필드 (기존 유지)
```
- 스캔 버튼 → `GET /scan?force=true` 호출
- COM 항목 선택: `form.type='balance', form.com=port`
- SiLA2 항목 선택: `form.type='balance', form.grpc_host=host, form.grpc_port=port` (com 없음)
- [SIM] 뱃지로 시뮬레이터 구분 (`simulator=true` TXT record 기준)

### 수락 기준
- 시뮬레이터 실행 → DevicesPage 스캔 → 드롭다운에 시뮬레이터 표시
- 시뮬레이터 선택 후 "추가" → balance 장치 등록, com 필드 없음
- 등록 후 ss_manager 재시작 시 subprocess 없이 연결 성공
- COM 포트도 드롭다운에 표시됨 (포트가 없으면 목록 비어 있음)
- mDNS 차단 환경: 수동 입력 필드로 여전히 등록 가능

### 검증
```bash
# 시뮬레이터 실행
python -m simulator --device balance --port 50051 --name "Sim-Balance-01"

# DevicesPage → [스캔] 클릭
# → "◈ Sim-Balance-01 :50051 [SIM]" 표시 확인
# → 선택 → 추가 → 장치 목록에 표시
# → ss_manager 재시작 → 장치 연결 확인
```

---

## [Checkpoint B]

- [ ] 시뮬레이터 mDNS 등록 확인 (로그)
- [ ] `/api/scan` 응답에 시뮬레이터 포함
- [ ] DevicesPage 스캔 버튼으로 발견 후 등록 성공
- [ ] 등록된 장치로 ss_manager 재시작 → 무게값 수신 확인

---

## T3 — Furnace 시뮬레이터

**목표**: 전기로 SiLA2 서버를 시뮬레이션한다. DevicesPage 스캔에서 furnace 타입으로 표시된다.

### 작업 내용

**3-A. 스파이크: sila2.code_generator 검증** ⚠️ HIGH RISK
```bash
# 시도
python -m sila2.code_generator --help
# 성공 시: TemperatureController.sila.xml 작성 후 생성
# 실패 시: 수동으로 base 클래스 + types 작성
```

`TemperatureController.sila.xml` 최소 정의:
- Observable Property: `CurrentTemperature` (Real, °C)
- Observable Property: `TargetTemperature` (Real, °C)
- Observable Property: `State` (String: idle/heating/holding/cooling)
- Command: `SetTargetTemperature` (param: Real)

**3-B. `devices/furnace.py` 구현**
```python
class FurnaceSimImpl(TemperatureControllerBase):
    _current_temp: float = 25.0
    _target_temp: float = 25.0
    τ = 120.0  # 시정수 (초)

    def _push_loop(self):
        # 1s 간격
        # dT = (target - current) / τ + gaussian(0, 0.1)
        # current += dT
        # state = idle|heating|holding|cooling 판단
        # update_CurrentTemperature, update_TargetTemperature, update_State

    def SetTargetTemperature(self, TargetTemperature: float, ...):
        self._target_temp = TargetTemperature
```

**3-C. `simulator/main.py` furnace 분기 추가**
- `--device furnace` 선택 시 FurnaceSimImpl + TemperatureControllerFeature 사용

**3-D. DevicesPage.vue furnace 표시**
- 스캔 결과에서 `device_type=furnace` 항목: `◈ Sim-Furnace-01 :50052 [SIM/FURNACE]`
- 선택 시 `form.type='generic_sila', form.host=host, form.port=port` (ss_manager 클라이언트 미구현)
- 경고 표시: "전기로 연결 클라이언트 미구현 — 표시만 가능"

### 수락 기준
- `python -m simulator --device furnace --port 50052` 실행 성공
- 스캔 시 furnace 항목 표시됨
- 목표 온도 25°C → 500°C 설정 시 1차 지연계 수렴 동작 (테스트로 확인)
- Ctrl+C 정상 종료

### 스파이크 fallback
sila2.code_generator 실패 시:
- `generated/temperaturecontroller/` 수동 작성 (base.py + types.py + xml)
- balance_server.py의 generated/ 패턴을 참고하여 최소한으로 구현

---

## T4 — Rich TUI

**목표**: 시뮬레이터 실행 중 현재 상태를 Rich Live로 시각적으로 표시한다.

### 작업 내용

**4-A. 장치별 패널 렌더 함수 분리**
```python
def _make_balance_panel(impl, name, host, port, start_time) -> Table:
    # 이름, 포트, Weight(g), 업타임

def _make_furnace_panel(impl, name, host, port, start_time) -> Table:
    # 이름, 포트, CurrentTemperature(°C), Setpoint(°C), 업타임
```
- `impl._model.get_weight()` / `impl._model.current_temperature` 직접 읽기 (lock-safe)
- 업타임: `time.time() - start_time` (프로세스 시작 기준)

**4-B. Rich Live 루프 통합**
```python
with Live(panel, refresh_per_second=4) as live:
    while True:
        live.update(make_panel())
        time.sleep(0.25)
```
- `_run_balance` / `_run_furnace` 각각에 통합 (while True 교체)

**4-C. Ctrl+C 처리 — impl.stop() + server.stop()**
```python
except KeyboardInterrupt:
    impl.stop()
    server.stop()   # ⚠️ 현재 누락 — gRPC 서버 종료 필요
    logger.info("[balance/furnace] 시뮬레이터 종료")
```
> Opus 위험 분석: 현재 코드는 `impl.stop()`만 호출하고 `server.stop()` 누락.
> gRPC 서버가 종료되지 않아 포트가 점유된 채 남을 수 있음.

### 수락 기준
- 실행 시 Rich TUI 표시 (표 형태, 4회/초 갱신)
- balance: Weight 실시간 갱신
- furnace: CurrentTemperature + Setpoint 실시간 갱신
- Ctrl+C 시 server.stop() → 포트 즉시 해제 확인 (같은 포트 재실행 가능)

### 검증
```bash
python -m simulator --device balance --port 50057
# TUI 확인 후 Ctrl+C
python -m simulator --device balance --port 50057  # 같은 포트 재실행 성공 확인
```

---

## T5 — FurnaceClient (ss_manager)

**목표**: ss_manager가 furnace 시뮬레이터에 gRPC로 연결해 온도 데이터를 수신한다.

### 작업 내용

**5-A. `ss_manager/core/clients/furnace.py` 신규**

BalanceClient와 동일 구조:
```python
class FurnaceClient(DeviceClient):
    # reader thread → TemperatureController.CurrentTemperature.subscribe()
    # _setpoint 캐시: 연결 시 Setpoint.get() 한 번 호출 후 로컬 캐시
    # get_status() → {"connected": bool, "data": {"CurrentTemperature": float, "Setpoint": float}}
```

> Opus 위험 분석: Setpoint.get()을 매 tick 호출하면 gRPC 왕복 지연 발생.
> 연결 시 1회 + SetTemperature 명령 수신 시 캐시 업데이트로 처리.

**5-B. `send_command` 구현**
```python
def send_command(self, command, params):
    if command == "SetTemperature":
        target = params["target"]   # 명시적 키 매핑 ("target" → TargetTemperature)
        client.TemperatureController.SetTemperature(TargetTemperature=target)
        self._setpoint = target     # 캐시 업데이트
```
> Opus 위험 분석: `"target"` vs `TargetTemperature` 파라미터 불일치 주의.

**5-C. `tests/test_furnace_client.py` 신규**

BalanceClient 테스트 패턴 동일 — `_client_factory` DI로 mock SilaClient 주입:
- 연결/단절 상태 전환
- CurrentTemperature 구독 → `get_status()` 반영
- SetTemperature 명령 → Setpoint 캐시 업데이트

### 수락 기준
- mock 기반 단위 테스트 통과
- 실제 furnace 시뮬레이터에 연결해 `get_status()` 에서 온도값 확인

---

## T6 — ss_manager lifespan furnace 지원

**목표**: ss_manager 시작 시 furnace 장치가 등록되어 있으면 FurnaceClient를 자동으로 시작한다.

### 작업 내용

**6-A. `_clients` 타입 확장**
```python
# 변경 전
_clients: dict[str, BalanceClient] = {}

# 변경 후
_clients: dict[str, DeviceClient] = {}
```
> Opus 위험 분석: 변경 전 `_clients[id]`를 통한 BalanceClient-특화 속성 접근이 있는지
> 먼저 grep 필수. 확인 후 타입 주석만 변경 (런타임 동작 무변경).

**6-B. lifespan furnace 분기 추가**
```python
for cfg in _registry.get_all():
    if cfg.type == "balance" and cfg.enabled:
        # 기존 balance 로직 유지
    elif cfg.type == "furnace" and cfg.enabled:
        client = FurnaceClient(cfg.id, cfg.name, cfg.config)
        await client.start()
        _clients[cfg.id] = client
        logger.info("[main] FurnaceClient 시작: %s", cfg.id)
```
- fail-soft: 연결 실패해도 exception을 잡아 log만 남기고 나머지 장치 계속 시작
- 여러 장치 동시 지원 (balance 1개 제한 제거)

**6-C. 테스트 업데이트**
- `test_main.py`: furnace 장치 추가 → lifespan 후 `_clients`에 포함 확인

### 수락 기준
- balance + furnace 동시 등록 후 ss_manager 시작 → 두 클라이언트 모두 연결
- 기존 balance 41개 테스트 전부 회귀 없음

---

## [Checkpoint C] — E2E 전체 흐름 검증

**목표**: balance + furnace 시뮬레이터 → scan → 등록 → 실시간 데이터 수신 전 과정 확인.

### 검증 시나리오

```
1. 시뮬레이터 실행
   python -m simulator --device balance --port 50057 --name "Sim-Balance-01"
   python -m simulator --device furnace --port 50058 --name "Sim-Furnace-01"

2. ss_manager 시작 (장치 없이)
   cd ss_manager/gui && pnpm electron:dev

3. DevicesPage → [스캔]
   → Sim-Balance-01 (balance) 발견 → [등록]
   → Sim-Furnace-01 (furnace) 발견 → [등록]

4. ss_manager 재시작
   → balance: connected, Weight 수신 확인
   → furnace: connected, CurrentTemperature 수신 확인

5. Rich TUI 확인
   → 두 터미널에서 TUI 값 갱신 실시간 확인

6. Ctrl+C 종료
   → ss_manager에서 장치 OFFLINE 전환 확인
```

### 체크리스트
- [ ] balance 시뮬레이터 TUI 정상 표시
- [ ] furnace 시뮬레이터 TUI 정상 표시
- [ ] /scan에서 두 장치 모두 발견
- [ ] DevicesPage 스캔 다이얼로그에서 등록 성공
- [ ] ss_manager 재시작 후 두 장치 CONNECTED
- [ ] Ctrl+C 후 포트 즉시 재사용 가능

---

## 테스트 계획

| 파일 | 테스트 내용 |
|------|-----------|
| `tests/test_balance_sim.py` | BalanceModel 단위 테스트 ✅ |
| `tests/test_furnace_sim.py` | FurnaceModel 단위 테스트 ✅ |
| `ss_manager/core/tests/test_scan.py` | scan_all mock 테스트 ✅ |
| `ss_manager/core/tests/test_furnace_client.py` | FurnaceClient DI mock 테스트 (신규) |
| `ss_manager/core/tests/test_main.py` | furnace lifespan 분기 테스트 (추가) |

---

## 위험 요소 및 대응

| 위험 | 대응 |
|------|------|
| `server.stop()` API 없음 | SilaServer stop 메서드 확인 — 없으면 gRPC channel 직접 종료 |
| `_clients` 타입 확장 시 콜 사이트 깨짐 | 변경 전 `grep "_clients\[" *.py` 필수 |
| Setpoint gRPC 지연 | 연결 시 1회 캐시, SetTemperature 시 캐시 업데이트 |
| Windows Ctrl+C + Rich Live | KeyboardInterrupt는 Windows에서 flaky — signal.signal(SIGINT) 백업 |
| 여러 balance 동시 등록 시 기존 "1개만 지원" 제한 제거 | lifespan loop 리팩토링으로 처리 |
