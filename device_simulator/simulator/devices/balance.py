"""CB310 저울 SiLA2 시뮬레이터.

balance_server.py의 역할을 COM 포트 없이 대체한다.
"""
from __future__ import annotations

import random
import threading
import time
from typing import TYPE_CHECKING

from simulator.devices.generated.weightmeasurement import (
    WeightMeasurementBase,
    WeightMeasurementFeature,
    SetZero_Responses,
)

if TYPE_CHECKING:
    from sila2.server import MetadataDict, SilaServer


class BalanceModel:
    """순수 시뮬레이션 모델 — SiLA2 의존성 없음. 단위 테스트 가능."""

    _MIN_NOISE = 0.01  # 최소 노이즈 σ (g)

    def __init__(self) -> None:
        self._offset: float = 0.0
        self._lock = threading.Lock()

    def get_weight(self) -> float:
        """랜덤워크 노이즈 포함 무게값 반환 (g)."""
        with self._lock:
            σ = max(self._MIN_NOISE, 0.002 * abs(self._offset))
            step = random.gauss(0, σ) * 0.1  # 랜덤워크 스텝
            self._offset += step
            return round(self._offset, 4)

    def set_zero(self) -> None:
        """현재 오프셋을 0으로 리셋 (영점 조정)."""
        with self._lock:
            self._offset = 0.0


class BalanceSimImpl(WeightMeasurementBase):
    """WeightMeasurementBase 구현 — BalanceModel 기반 시뮬레이션."""

    _PUSH_INTERVAL = 0.05  # 50ms

    def __init__(self, parent_server: SilaServer) -> None:
        super().__init__(parent_server=parent_server)
        self._model = BalanceModel()
        self._running = True
        self._push_thread = threading.Thread(
            target=self._push_loop,
            name="balance-sim-push",
            daemon=True,
        )
        self._push_thread.start()

    def _push_loop(self) -> None:
        while self._running:
            weight = self._model.get_weight()
            try:
                self.update_Weight(weight)
            except Exception:
                pass  # 구독자 없을 때 무시
            time.sleep(self._PUSH_INTERVAL)

    def SetZero(self, *, metadata: MetadataDict) -> SetZero_Responses:
        self._model.set_zero()
        return SetZero_Responses()

    def stop(self) -> None:
        self._running = False

    @property
    def current_weight(self) -> float:
        return self._model.get_weight()
