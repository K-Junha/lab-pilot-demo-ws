"""BalanceModel 단위 테스트 — SiLA2 서버 불필요."""
from __future__ import annotations

import pytest

from simulator.devices.balance import BalanceModel


def test_initial_weight_is_zero():
    model = BalanceModel()
    assert model.get_weight() == pytest.approx(0.0, abs=0.5)


def test_set_zero_resets_offset():
    model = BalanceModel()
    # 랜덤워크를 여러 번 실행해 오프셋 누적
    for _ in range(100):
        model.get_weight()
    model.set_zero()
    # SetZero 이후 다음 값은 0 근처여야 함
    weight = model.get_weight()
    assert weight == pytest.approx(0.0, abs=0.5)


def test_successive_readings_differ():
    model = BalanceModel()
    readings = [model.get_weight() for _ in range(10)]
    # 모든 값이 동일하면 노이즈 없음 — 최소 하나는 달라야 함
    assert len(set(round(r, 6) for r in readings)) > 1


def test_noise_is_bounded():
    model = BalanceModel()
    # base_weight=0 에서 노이즈는 최소값(0.01g) 기준
    readings = [model.get_weight() for _ in range(200)]
    # 200번 랜덤워크에서 ±5g을 벗어날 확률은 극히 낮음
    assert all(-5.0 < r < 5.0 for r in readings)
