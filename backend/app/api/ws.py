"""WebSocket 엔드포인트 — SiLA 저울 실시간 무게 스트리밍"""
from __future__ import annotations

import asyncio
import logging
import math
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.config import settings

router = APIRouter(tags=["ws"])
logger = logging.getLogger(__name__)

# SiLA 서버 기본 설정
BALANCE_HOST = "127.0.0.1"
BALANCE_PORT = 50051

# 전용 executor: 스레드 누수 방지
_ws_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="sila-ws")

WEIGHT_READ_TIMEOUT = 3.0  # 첫 답 타임아웃 (sec)
AUTH_TIMEOUT = 5.0          # JWT 첫 메시지 대기 타임아웃 (sec)


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
        import json
        msg = json.loads(raw)
        if msg.get("type") != "auth" or not msg.get("token"):
            raise ValueError("missing token")
        jwt.decode(msg["token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (JWTError, ValueError, Exception):
        await websocket.send_json({"type": "error", "message": "Unauthorized"})
        await websocket.close(code=4401)
        return False

    return True


@router.websocket("/ws/balance")
async def balance_ws(websocket: WebSocket):
    """SiLA 저울 서버에 연결하여 무게 데이터를 WebSocket으로 스트리밍.

    클라이언트가 WebSocket 연결 → JWT 첫 메시지 인증 → SiLA gRPC subscribe → 무게 값 전달.
    """
    await websocket.accept()
    logger.info("[WS] Balance WebSocket client connected")

    if not await _authenticate_ws(websocket):
        logger.warning("[WS] JWT 인증 실패 — 연결 종료")
        return

    client = None
    try:
        from sila2.client import SilaClient

        client = SilaClient(BALANCE_HOST, BALANCE_PORT, insecure=True)
        weight_property = client.WeightMeasurement.Weight
        subscription = weight_property.subscribe()

        while True:
            try:
                # 주어진 timeout 내에 값이 오지 않으면 클라이언트에 오류 전송 후 진행
                value = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        _ws_executor, lambda: next(subscription)
                    ),
                    timeout=WEIGHT_READ_TIMEOUT,
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "error", "message": "Balance read timeout"})
                continue

            # NaN = 저울 미연결 신호
            if math.isnan(value):
                await websocket.send_json({"type": "disconnected"})
            else:
                await websocket.send_json({
                    "type": "weight",
                    "value": round(value, 4),
                })
    except WebSocketDisconnect:
        logger.info("[WS] Balance WebSocket client disconnected")
    except StopIteration:
        logger.warning("[WS] SiLA subscription ended")
        try:
            await websocket.send_json({"type": "error", "message": "SiLA subscription ended"})
        except Exception:
            pass
    except Exception as e:
        logger.error(f"[WS] Error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": "Internal server error"})
        except Exception:
            pass
    finally:
        if client:
            try:
                del client
            except Exception:
                pass
        logger.info("[WS] Balance WebSocket session closed")
