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

from rich.console import Console
from rich.live import Live
from rich.table import Table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("simulator")
console = Console()


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _fmt_uptime(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _make_balance_panel(impl, name: str, host: str, port: int, start: float) -> Table:
    weight = impl._model.get_weight()
    uptime = time.time() - start

    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("key", style="dim")
    t.add_column("value", style="bold")
    t.add_row("Device", f"[cyan]{name}[/cyan]  [dim]balance[/dim]")
    t.add_row("gRPC", f"{host}:{port}")
    t.add_row("Weight", f"[green]{weight:+.4f}[/green] g")
    t.add_row("Uptime", _fmt_uptime(uptime))
    t.add_row("", "[dim]Ctrl+C to stop[/dim]")
    return t


def _make_furnace_panel(impl, name: str, host: str, port: int, start: float) -> Table:
    temp = impl._model.current_temperature
    setpoint = impl._model.setpoint
    uptime = time.time() - start

    temp_color = "red" if temp > setpoint + 1 else ("yellow" if abs(temp - setpoint) > 1 else "green")

    t = Table(show_header=False, box=None, padding=(0, 2))
    t.add_column("key", style="dim")
    t.add_column("value", style="bold")
    t.add_row("Device", f"[cyan]{name}[/cyan]  [dim]furnace[/dim]")
    t.add_row("gRPC", f"{host}:{port}")
    t.add_row("Temp", f"[{temp_color}]{temp:6.1f}[/{temp_color}] °C")
    t.add_row("Setpoint", f"{setpoint:6.1f} °C")
    t.add_row("Uptime", _fmt_uptime(uptime))
    t.add_row("", "[dim]Ctrl+C to stop[/dim]")
    return t


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

    start = time.time()
    try:
        with Live(console=console, refresh_per_second=4, screen=False) as live:
            while True:
                live.update(_make_balance_panel(impl, name, host, actual_port, start))
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        impl.stop()
        server.stop()
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

    start = time.time()
    try:
        with Live(console=console, refresh_per_second=4, screen=False) as live:
            while True:
                live.update(_make_furnace_panel(impl, name, host, actual_port, start))
                time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        impl.stop()
        server.stop()
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
