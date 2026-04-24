"""FurnaceModel 단위 테스트 — SiLA2 의존성 없음."""
from __future__ import annotations

import time

import pytest

from simulator.devices.furnace import FurnaceModel


def test_initial_temperature_is_ambient():
    model = FurnaceModel(ambient=25.0)
    assert model.current_temperature == pytest.approx(25.0, abs=0.01)


def test_initial_setpoint_is_ambient():
    model = FurnaceModel(ambient=25.0)
    assert model.setpoint == 25.0


def test_set_setpoint_updates_target():
    model = FurnaceModel(ambient=25.0)
    model.set_setpoint(500.0)
    assert model.setpoint == 500.0


def test_tick_moves_toward_setpoint():
    model = FurnaceModel(ambient=25.0, tau=1.0)
    model.set_setpoint(100.0)
    time.sleep(0.1)
    temp = model.tick()
    assert temp > 25.0, "온도가 목표 방향으로 증가해야 한다"
    assert temp < 100.0, "아직 목표에 도달하지 않아야 한다"


def test_tick_converges_with_large_dt():
    """tau 대비 매우 큰 dt이면 setpoint에 거의 수렴한다."""
    model = FurnaceModel(ambient=25.0, tau=1.0)
    model.set_setpoint(200.0)
    time.sleep(10)  # 10 * tau
    temp = model.tick()
    assert temp == pytest.approx(200.0, abs=1.0)


def test_tick_no_change_when_at_setpoint():
    model = FurnaceModel(ambient=100.0, tau=5.0)
    model.set_setpoint(100.0)
    time.sleep(0.05)
    temp = model.tick()
    assert temp == pytest.approx(100.0, abs=0.01)


def test_cooling_when_setpoint_lower():
    model = FurnaceModel(ambient=200.0, tau=1.0)
    model.set_setpoint(25.0)
    time.sleep(0.1)
    temp = model.tick()
    assert temp < 200.0, "목표가 낮으면 온도가 내려가야 한다"
