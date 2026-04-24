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

**4-A. `simulator/main.py` TUI 통합**
```python
from rich.live import Live
from rich.table import Table
from rich.console import Console

# 메인 스레드에서 Live 실행
# SilaServer + push_loop + mDNS는 bg thread로 이동 (이미 daemon)

def make_table(impl) -> Table:
    # 장치 이름, 타입, 포트
    # 현재 값 (무게 g / 온도 °C)
    # mDNS 등록 상태 (✓ / ✗)
    # Ctrl+C 안내
```

**4-B. Ctrl+C 처리**
```python
try:
    with Live(make_table(impl), refresh_per_second=4) as live:
        while True:
            live.update(make_table(impl))
            time.sleep(0.25)
except KeyboardInterrupt:
    mdns.unregister()
    # push_loop thread는 daemon이므로 자동 종료
```

### 수락 기준
- 실행 시 Rich TUI 표시 (표 형태)
- 무게/온도 값이 실시간 갱신 (4회/초)
- mDNS 등록 상태 표시
- Ctrl+C 시 mDNS unregister 후 정상 종료

---

## 테스트 계획

| 파일 | 테스트 내용 |
|------|-----------|
| `tests/test_balance_sim.py` | SiLA2 클라이언트로 구독, 10회 수신 확인, SetZero 후 0 근처 확인 |
| `tests/test_furnace_sim.py` | 목표 온도 설정, t=300s 수렴 확인 (단위 테스트, gRPC 불필요) |
| `tests/test_mdns.py` | register → ServiceBrowser 발견 확인 → unregister → 사라짐 확인 |
| `ss_manager/core/tests/test_scan.py` | mock comports + mock zeroconf, scan_all 응답 형식 검증 |

---

## 위험 요소 및 대응

| 위험 | 대응 |
|------|------|
| Furnace sila2.code_generator 실패 | T3-A 스파이크 먼저 — 실패 시 수동 스텁 fallback |
| mDNS Windows Firewall 차단 | 수동 입력 필드 유지, 문서에 방화벽 허용 규칙 안내 |
| WeightMeasurement XML 변경 시 불일치 | generated/ 복사본에 주석으로 원본 경로 명시 |
| SilaServer.start_insecure 블로킹 여부 | T1 구현 시 즉시 검증 (balance_server.py 패턴 참고) |
