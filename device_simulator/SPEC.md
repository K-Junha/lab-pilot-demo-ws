# SPEC — Device Simulator

> 최종 업데이트: 2026-04-23

## 1. Objective

실제 하드웨어(저울, 전기로)가 없는 환경에서 ss_manager와 lab-pilot이 정상 동작하도록 가상 SiLA2 장치를 제공한다.

**대상 사용자:** 개발자, 데모 시연자
**핵심 가치:** ss_manager 코드 변경 최소화 — 시뮬레이터가 real device와 동일한 SiLA2 gRPC 인터페이스를 제공하므로, ss_manager BalanceClient는 차이를 인식하지 못한다.

### 시스템 전체 흐름

```
[device_simulator]          [ss_manager]              [lab-pilot]
 balance sim :50051  ←gRPC→  BalanceClient   ←WS:8765→  WeighingRunner
 furnace sim :50052  ←gRPC→  (향후 구현)
           │
           └─ mDNS 등록 (_sila._tcp.local.)
                    ↑
             ss_manager /api/scan 이 발견
```

### 실제 하드웨어 흐름 (참고)

```
[CB310 저울] ←serial→ [balance_server.py] ←gRPC:50051→ [ss_manager BalanceClient]
```

시뮬레이터는 balance_server.py의 역할을 대체한다. COM 포트는 사용하지 않는다.

---

## 2. 범위

### Part 1 — device_simulator (신규 프로젝트)

- `--device balance` : CB310 저울 SiLA2 서버 시뮬레이션
- `--device furnace` : 전기로 온도 컨트롤러 SiLA2 서버 시뮬레이션
- mDNS 자동 등록 (`_sila._tcp.local.`)
- Rich TUI: 현재 시뮬레이션 값 실시간 표시

### Part 2 — ss_manager 수정 (최소 변경)

- `GET /api/scan` 엔드포인트 추가 (COM 포트 목록 + mDNS 발견 SiLA2 서비스)
- `main.py` lifespan 수정: balance config에 `com` 없으면 subprocess 미실행, gRPC 직접 연결
- `DevicesPage.vue` 수정: 스캔 버튼 + 드롭다운으로 장치 선택

---

## 3. 프로젝트 구조

```
WS/
├── device_simulator/               ← 신규
│   ├── SPEC.md
│   ├── pyproject.toml
│   ├── simulator/
│   │   ├── __init__.py
│   │   ├── main.py                 ← CLI 진입점 (argparse + Rich TUI)
│   │   ├── mdns.py                 ← zeroconf ServiceInfo 등록/해제
│   │   └── devices/
│   │       ├── __init__.py
│   │       ├── balance.py          ← WeightMeasurement SiLA2 서버
│   │       └── furnace.py          ← TemperatureController SiLA2 서버
│   └── tests/
│       ├── test_balance_sim.py
│       └── test_mdns.py
│
└── ss_manager/
    ├── core/
    │   ├── scan.py                 ← 신규: COM 포트 스캔 + mDNS 브라우저
    │   └── main.py                 ← 수정: /api/scan 엔드포인트, lifespan 조건부 분기
    └── gui/src/pages/
        └── DevicesPage.vue         ← 수정: 스캔 버튼 + 발견 장치 드롭다운
```

---

## 4. 상세 설계

### 4-1. device_simulator CLI

```bash
python -m simulator --device balance --port 50051 --name "Sim-Balance-01"
python -m simulator --device furnace --port 50052 --name "Sim-Furnace-01"
```

| 인자 | 기본값 | 설명 |
|------|--------|------|
| `--device` | (필수) | `balance` \| `furnace` |
| `--port` | `0` | 0이면 빈 포트 자동 선택 |
| `--name` | `Sim-{Device}-01` | mDNS에 등록될 장치 이름 |
| `--host` | `127.0.0.1` | gRPC 바인딩 주소 |

실행 시 Rich TUI로 다음을 표시:
- 장치 이름, 타입, 포트
- 현재 시뮬레이션 값 (무게 g / 온도 °C)
- 연결된 gRPC 클라이언트 수
- mDNS 등록 상태
- Ctrl+C로 정상 종료

### 4-2. Balance Simulator (`devices/balance.py`)

SiLA2 WeightMeasurement Feature 구현 (`ss_manager/core/balance/generated/` 재사용):

| 인터페이스 | 동작 |
|-----------|------|
| `Weight` (Observable Property) | 50ms 간격으로 랜덤워크 무게값 푸시. 노이즈 ±0.5% |
| `SetZero` (Command) | 내부 기준값을 현재값으로 설정 (0점 조정 시뮬레이션) |

시뮬레이션 모델:
```
weight(t) = base_weight + gaussian_noise(0, σ)
σ = 0.002 * base_weight  # 0.2% 노이즈
```
`base_weight` 초기값 = 0.0g, SetZero 시 현재 누적 오프셋을 0으로 리셋.

### 4-3. Furnace Simulator (`devices/furnace.py`)

신규 SiLA2 TemperatureController Feature 정의:

| 인터페이스 | 동작 |
|-----------|------|
| `CurrentTemperature` (Observable Property) | 1s 간격으로 현재 온도 푸시 |
| `TargetTemperature` (Observable Property) | 설정 온도 푸시 |
| `SetTarget` (Command) | 목표 온도 설정 |
| `State` (Observable Property) | `idle` \| `heating` \| `holding` \| `cooling` |

시뮬레이션 모델 (1차 지연계):
```
dT/dt = (target - T) / τ + noise
τ = 120s  # 시정수 (실제 전기로 수준)
noise = gaussian(0, 0.1)  # ±0.1°C
```

### 4-4. mDNS 등록 (`mdns.py`)

`python-zeroconf` 사용. 서비스 타입: `_sila._tcp.local.`

TXT 레코드:
```
device_type = balance | furnace
sila_version = 2.0
simulator = true
```

등록 시점: gRPC 서버 ready 확인 후. 종료 시 `unregister()` 호출.

### 4-5. ss_manager `GET /api/scan`

`core/scan.py`:
```python
def scan_com_ports() -> list[dict]:
    # serial.tools.list_ports.comports() 사용
    # [{port: "COM3", description: "..."}, ...]

def scan_sila_services(timeout: float = 2.0) -> list[dict]:
    # zeroconf ServiceBrowser, _sila._tcp.local.
    # [{name: "Sim-Balance-01", host: "127.0.0.1", port: 50051, device_type: "balance"}, ...]
```

응답 형식:
```json
{
  "com_ports": [
    {"port": "COM3", "description": "USB Serial Port"}
  ],
  "sila_services": [
    {"name": "Sim-Balance-01", "host": "127.0.0.1", "port": 50051, "device_type": "balance"}
  ]
}
```

스캔 결과는 30초 캐시. 명시적 재스캔 시 캐시 무효화.

### 4-6. ss_manager `main.py` lifespan 수정

현재: balance 등록 시 항상 balance_server.py subprocess 실행
수정: `com` 필드 존재 여부로 분기

```python
# 수정 후 로직
if cfg.type == "balance" and cfg.enabled:
    if cfg.config.get("com"):
        # 실제 하드웨어: subprocess 실행 후 gRPC 연결
        _balance_proc = await _start_balance_subprocess(...)
        await asyncio.sleep(2)
    # 시뮬레이터: subprocess 없이 gRPC 직접 연결
    client = BalanceClient(cfg.id, cfg.name, cfg.config)
    await client.start()
```

balance config 등록 시:
- 실제 하드웨어: `{com: "COM11", grpc_port: 50051}`
- 시뮬레이터: `{grpc_host: "127.0.0.1", grpc_port: 50051}` (com 없음)

### 4-7. DevicesPage.vue 수정

장치 추가 다이얼로그에 스캔 섹션 추가:

```
[스캔] 버튼
─────────────────────────
● COM3 — USB Serial Port     ← pyserial
◈ Sim-Balance-01 :50051      ← mDNS (simulator=true 표시)
```

- 항목 선택 시 `form.type`, `form.com` / `form.grpc_host`, `form.grpc_port` 자동 입력
- 스캔 결과 없으면 "발견된 장치 없음" 표시
- mDNS가 차단된 환경을 위해 수동 입력 필드는 유지

---

## 5. 기술 스택

| 영역 | 기술 |
|------|------|
| 시뮬레이터 언어 | Python 3.11+ |
| SiLA2 프레임워크 | `sila2` (기존 ss_manager와 동일) |
| mDNS | `zeroconf` (python-zeroconf) |
| TUI | `rich` |
| CLI | `argparse` |
| ss_manager 수정 | Python (FastAPI) + Vue/Quasar (기존) |
| COM 포트 스캔 | `pyserial` |

---

## 6. 의존성

```toml
# device_simulator/pyproject.toml
[project]
dependencies = [
    "sila2>=0.10",
    "zeroconf>=0.115",
    "rich>=13",
    "pyserial>=3.5",  # 스캔 UI 선택사항
]
```

ss_manager에 추가:
```toml
"zeroconf>=0.115"  # ss_manager/core/pyproject.toml
```

---

## 7. 테스트 전략

| 테스트 | 방법 |
|--------|------|
| balance sim 데이터 생성 | `test_balance_sim.py`: SiLA2 클라이언트로 직접 구독, 10회 수신 확인 |
| SetZero 동작 | 명령 후 오프셋 0 확인 |
| furnace 모델 | 목표 온도 수렴 시뮬레이션 (t=300s) |
| mDNS 등록/해제 | `test_mdns.py`: ServiceBrowser로 발견 확인 후 종료 시 사라짐 확인 |
| `/api/scan` | ss_manager 단위 테스트: mock zeroconf + mock pyserial |
| lifespan 분기 | `com` 있을 때/없을 때 subprocess 실행 여부 확인 |

---

## 8. 실행 방법 (완성 후)

```bash
# 시뮬레이터 실행
cd device_simulator
pip install -e .
python -m simulator --device balance --port 50051

# ss_manager 실행 (변경 없음)
cd ss_manager/gui && pnpm electron:dev

# DevicesPage에서 [스캔] → Sim-Balance-01 선택 → 추가
```

---

## 9. Boundaries

### Never
- `device_simulator`에서 `ss_manager` 패키지를 직접 import 금지 (gRPC/mDNS 인터페이스만 사용)
- 시뮬레이터에서 실제 COM 포트 쓰기 금지
- 발견된 장치를 사용자 확인 없이 자동 등록 금지
- 시뮬레이터 상태를 파일에 영속화 금지 (재시작 시 초기값으로 리셋)

### Ask First
- 세 번째 장치 타입 추가 시 (scope creep)
- SiLA2 Feature XML 계약 변경 시 (BalanceClient에 영향)
- mDNS를 커스텀 디스커버리로 교체 시
- 시뮬레이터에 웹 UI 추가 시
- ss_manager에서 시뮬레이터 프로세스를 자동 실행하도록 변경 시
