"""device_simulator CLI 진입점.

실행:
    python -m simulator --device balance --port 50051
    python -m simulator --device balance  # 빈 포트 자동 선택
"""
from __future__ import annotations

import argparse
import logging
import socket
import sys
import time
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("simulator")


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _run_balance(host: str, port: int, name: str) -> None:
    from sila2.server import SilaServer
    from simulator.devices.balance import BalanceSimImpl
    from simulator.devices.generated.weightmeasurement import WeightMeasurementFeature

    server = SilaServer(
        server_name=name,
        server_description="Virtual CB310 Balance Simulator",
        server_type="LaboratoryBalance",
        server_version="0.1",
        server_vendor_url="https://github.com/K-Junha/lab-pilot-demo-ws",
        server_uuid=uuid4(),
    )
    impl = BalanceSimImpl(server)
    server.set_feature_implementation(WeightMeasurementFeature, impl)

    actual_port = port if port != 0 else _find_free_port()
    server.start_insecure(host, actual_port)
    logger.info("[balance] 시뮬레이터 시작: %s:%d (%s)", host, actual_port, name)

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    print(f"\n  Balance Simulator -- {name}")
    print(f"  gRPC: {host}:{actual_port}")
    print("  Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        impl.stop()
        logger.info("[balance] 시뮬레이터 종료")


def _run_furnace(host: str, port: int, name: str) -> None:
    from sila2.server import SilaServer
    from simulator.devices.furnace import FurnaceSimImpl
    from simulator.devices.generated.temperaturecontroller import TemperatureControllerFeature

    server = SilaServer(
        server_name=name,
        server_description="Virtual Furnace Temperature Controller",
        server_type="TemperatureController",
        server_version="0.1",
        server_vendor_url="https://github.com/K-Junha/lab-pilot-demo-ws",
        server_uuid=uuid4(),
    )
    impl = FurnaceSimImpl(server)
    server.set_feature_implementation(TemperatureControllerFeature, impl)

    actual_port = port if port != 0 else _find_free_port()
    server.start_insecure(host, actual_port)
    logger.info("[furnace] 시뮬레이터 시작: %s:%d (%s)", host, actual_port, name)

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    print(f"\n  Furnace Simulator -- {name}")
    print(f"  gRPC: {host}:{actual_port}")
    print("  Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        impl.stop()
        logger.info("[furnace] 시뮬레이터 종료")


def main() -> None:
    parser = argparse.ArgumentParser(description="Virtual SiLA2 Device Simulator")
    parser.add_argument("--device", required=True, choices=["balance", "furnace"],
                        help="시뮬레이션할 장치 타입")
    parser.add_argument("--port", type=int, default=0,
                        help="gRPC 포트 (0=자동)")
    parser.add_argument("--name", default=None,
                        help="장치 이름 (기본값: Sim-Balance-01 등)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="바인딩 호스트")
    args = parser.parse_args()

    if args.device == "balance":
        name = args.name or "Sim-Balance-01"
        _run_balance(args.host, args.port, name)
    elif args.device == "furnace":
        name = args.name or "Sim-Furnace-01"
        _run_furnace(args.host, args.port, name)


if __name__ == "__main__":
    main()
