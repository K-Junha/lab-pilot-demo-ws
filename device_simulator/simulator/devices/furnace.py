"""Furnace 시뮬레이터 — 1차 지연계 열 모델."""
from __future__ import annotations

import math
import threading
import time

from sila2.server import MetadataDict

from simulator.devices.generated.temperaturecontroller import (
    SetTemperature_Responses,
    TemperatureControllerBase,
    TemperatureControllerFeature,  # noqa: F401  (re-exported for main.py)
)

_AMBIENT_TEMP = 25.0
_TAU = 30.0          # 열 시정수 (초) — 데모용 단축 값
_PUSH_INTERVAL = 0.05


class FurnaceModel:
    """1차 지연계(first-order lag) 열 모델.

    τ=30 s 시정수로 목표 온도에 지수적으로 수렴.
    SiLA2 의존성 없음 — 단위 테스트 가능.
    """

    def __init__(self, ambient: float = _AMBIENT_TEMP, tau: float = _TAU) -> None:
        self._tau = tau
        self._lock = threading.Lock()
        self._current = ambient
        self._setpoint = ambient
        self._last_tick = time.monotonic()

    def tick(self) -> float:
        """경과 시간 기반으로 온도를 갱신하고 현재 온도를 반환한다."""
        with self._lock:
            now = time.monotonic()
            dt = now - self._last_tick
            self._last_tick = now
            alpha = 1.0 - math.exp(-dt / self._tau)
            self._current += alpha * (self._setpoint - self._current)
            return round(self._current, 2)

    def set_setpoint(self, target: float) -> None:
        with self._lock:
            self._setpoint = float(target)

    @property
    def setpoint(self) -> float:
        with self._lock:
            return self._setpoint

    @property
    def current_temperature(self) -> float:
        with self._lock:
            return round(self._current, 2)


class FurnaceSimImpl(TemperatureControllerBase):
    """SiLA2 TemperatureController 구현체."""

    def __init__(self, parent_server) -> None:
        super().__init__(parent_server=parent_server)
        self._model = FurnaceModel()
        self._running = True
        self._push_thread = threading.Thread(
            target=self._push_loop,
            name="furnace-sim-push",
            daemon=True,
        )
        self._push_thread.start()

    def _push_loop(self) -> None:
        while self._running:
            temp = self._model.tick()
            try:
                self.update_CurrentTemperature(temp)
            except Exception:
                pass
            time.sleep(_PUSH_INTERVAL)

    def get_Setpoint(self, *, metadata: MetadataDict) -> float:
        return self._model.setpoint

    def SetTemperature(
        self, TargetTemperature: float, *, metadata: MetadataDict
    ) -> SetTemperature_Responses:
        self._model.set_setpoint(TargetTemperature)
        return SetTemperature_Responses()

    def stop(self) -> None:
        self._running = False
