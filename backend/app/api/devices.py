"""장비 상태 REST API"""
from __future__ import annotations

import asyncio
import math
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

router = APIRouter(tags=["devices"])

# SiLA 서버 연결 정보 (추후 DB/설정 파일로 관리)
SILA_SERVERS = {
    "balance": {
        "id": "balance",
        "name": "CB310 저울",
        "type": "balance",
        "host": "127.0.0.1",
        "port": 50051,
    },
}

_executor = ThreadPoolExecutor(max_workers=4)


def _check_balance_connection(host: str, port: int) -> dict:
    """SiLA gRPC Weight 값을 실제로 구독해 저울 물리 연결 여부를 확인.

    - SiLA 서버 자체에 접속이 안 되면 connected=False
    - 접속은 되지만 2초 내 Weight 값이 오지 않으면 connected=False (저울 미연결)
    - Weight 값이 정상 수신되면 connected=True
    """
    import queue
    import threading

    try:
        from sila2.client import SilaClient
        client = SilaClient(host, port, insecure=True)
    except Exception:
        return {"connected": False, "detail": "SiLA server not reachable"}

    result_q: queue.Queue = queue.Queue()

    def _read_weight():
        try:
            subscription = client.WeightMeasurement.Weight.subscribe()
            value = next(subscription)
            result_q.put(("ok", value))
        except Exception as e:
            result_q.put(("error", str(e)))

    t = threading.Thread(target=_read_weight, daemon=True)
    t.start()

    try:
        status, payload = result_q.get(timeout=2.0)
    except queue.Empty:
        del client
        return {"connected": False, "detail": "No weight data within timeout (balance not connected)"}

    del client
    if status == "ok":
        if math.isnan(payload):
            return {"connected": False, "detail": "Balance not physically connected (NaN)"}
        return {"connected": True, "weight": round(payload, 4)}
    return {"connected": False, "detail": f"Weight read failed: {payload}"}


@router.get("/devices")
async def list_devices():
    """등록된 SiLA 장비 목록 반환."""
    return list(SILA_SERVERS.values())


@router.get("/devices/{device_id}/status")
async def device_status(device_id: str):
    """특정 장비의 연결 상태 확인.

    SiLA gRPC Weight Observable Property 구독으로 물리 장치 연결 여부까지 검증.
    """
    server = SILA_SERVERS.get(device_id)
    if not server:
        return {"error": "device not found"}, 404

    loop = asyncio.get_event_loop()
    result = await asyncio.wait_for(
        loop.run_in_executor(
            _executor,
            _check_balance_connection,
            server["host"],
            server["port"],
        ),
        timeout=5.0,
    )
    return {"id": device_id, **result}
