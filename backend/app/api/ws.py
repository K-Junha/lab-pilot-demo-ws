"""WebSocket 엔드포인트 — ss_manager 캐시 기반 저울 실시간 스트리밍"""
from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.config import settings
from app.core.logger import get_logger

router = APIRouter(tags=["ws"])
logger = get_logger("system")

AUTH_TIMEOUT = 5.0       # JWT 첫 메시지 대기 타임아웃 (sec)
POLL_INTERVAL = 0.5      # 캐시 폴링 간격 (sec)


async def _authenticate_ws(websocket: WebSocket) -> bool:
    """연결 후 첫 메시지로 JWT를 검증한다.

    프로토콜:
      클라이언트 → {"type": "auth", "token": "<JWT>"}
      실패 → {"type": "error", "message": "Unauthorized"} + close(4401)
      성공 → True 반환
    """
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=AUTH_TIMEOUT)
    except asyncio.TimeoutError:
        await websocket.send_json({"type": "error", "message": "Unauthorized"})
        await websocket.close(code=4401)
        return False

    try:
        msg = json.loads(raw)
        if msg.get("type") != "auth" or not msg.get("token"):
            raise ValueError("missing token")
        jwt.decode(msg["token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (JWTError, ValueError, Exception):
        await websocket.send_json({"type": "error", "message": "Unauthorized"})
        await websocket.close(code=4401)
        return False

    return True


def _find_balance_value() -> float | None:
    """인메모리 캐시에서 Weight 데이터를 보유한 장치를 탐색해 반환.

    device_id에 무관하게 online ss_manager의 연결된 장치 중
    latest_data["Weight"] 값이 있는 첫 번째 항목을 반환.
    없으면 None 반환.
    """
    from app.api.ws_manager_client import get_cache

    for cached in get_cache().values():
        if not cached.online:
            continue
        for dev in cached.devices.values():
            if dev.connected:
                weight = dev.latest_data.get("Weight")
                if weight is not None:
                    return float(weight)
    return None


@router.websocket("/ws/balance")
async def balance_ws(websocket: WebSocket):
    """ss_manager 캐시에서 무게 데이터를 읽어 WebSocket으로 스트리밍.

    클라이언트가 WebSocket 연결 → JWT 첫 메시지 인증 → 캐시 폴링 → 무게 값 전달.
    메시지 포맷: {"type":"weight","value":X} | {"type":"disconnected"}
    """
    await websocket.accept()
    logger.info("[WS] Balance WebSocket 클라이언트 연결")

    if not await _authenticate_ws(websocket):
        logger.warning("[WS] JWT 인증 실패 — 연결 종료")
        return

    try:
        while True:
            await asyncio.sleep(POLL_INTERVAL)

            value = _find_balance_value()
            if value is None:
                await websocket.send_json({"type": "disconnected"})
            else:
                await websocket.send_json({"type": "weight", "value": round(value, 4)})

    except WebSocketDisconnect:
        logger.info("[WS] Balance WebSocket 클라이언트 연결 해제")
    except Exception as e:
        logger.error("[WS] 오류: %s", e)
        try:
            await websocket.send_json({"type": "error", "message": "Internal server error"})
        except Exception:
            pass
    finally:
        logger.info("[WS] Balance WebSocket 세션 종료")
