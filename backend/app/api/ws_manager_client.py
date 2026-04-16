"""ss_manager WebSocket 클라이언트 + 인메모리 캐시.

각 등록된 ss_manager에 대해 asyncio.Task로 무한 재연결 루프를 유지한다.
런타임 상태(online, devices)는 DB에 persist하지 않고 인메모리 캐시에만 저장한다.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.logger import get_logger
from app.database import AsyncSessionLocal
from app.models.models import SsManager

logger = get_logger("system")

_RECONNECT_DELAY = 3  # seconds


@dataclass
class DeviceCache:
    id: str
    name: str
    icon: str
    connected: bool = False
    latest_data: dict = field(default_factory=dict)


@dataclass
class ManagerCache:
    manager_id: int
    name: str
    host: str
    ws_port: int
    api_key: str
    online: bool = False
    devices: dict[str, DeviceCache] = field(default_factory=dict)
    last_seen: datetime | None = None
    command_queue: asyncio.Queue = field(default_factory=asyncio.Queue)


# manager_id → ManagerCache
_cache: dict[int, ManagerCache] = {}

# manager_id → asyncio.Task (재연결 루프)
_tasks: dict[int, asyncio.Task] = {}


def get_cache() -> dict[int, ManagerCache]:
    """현재 인메모리 캐시 반환."""
    return _cache


def _handle_incoming(cache: ManagerCache, data: dict) -> None:
    """수신 메시지를 캐시에 반영한다."""
    msg_type = data.get("type")

    if msg_type == "device_data":
        device_id = data.get("device_id")
        if device_id and device_id in cache.devices:
            cache.devices[device_id].latest_data = data.get("data", {})
            cache.devices[device_id].connected = True

    elif msg_type == "device_status":
        device_id = data.get("device_id")
        if device_id and device_id in cache.devices:
            cache.devices[device_id].connected = data.get("connected", False)

    elif msg_type == "heartbeat":
        pass  # last_seen은 호출 전 이미 갱신됨


async def _connect_loop(manager_id: int) -> None:
    """단일 ss_manager에 대한 무한 재연결 루프."""
    try:
        import websockets  # type: ignore[import-untyped]
    except ImportError:
        logger.error("[ws_manager] websockets 패키지 미설치 — pip install websockets")
        return

    while True:
        cache = _cache.get(manager_id)
        if cache is None:
            break

        uri = f"ws://{cache.host}:{cache.ws_port}"
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                logger.info("[ws_manager] 연결 성공: manager_id=%d uri=%s", manager_id, uri)

                # 1. 인증 메시지 전송
                await ws.send(json.dumps({"type": "auth", "api_key": cache.api_key}))

                # 2. 인증 응답 대기
                raw = await asyncio.wait_for(ws.recv(), timeout=5)
                msg = json.loads(raw)
                if msg.get("type") != "auth_ok":
                    logger.warning("[ws_manager] 인증 실패: manager_id=%d msg=%s", manager_id, msg)
                    cache.online = False
                    await asyncio.sleep(_RECONNECT_DELAY)
                    continue

                # 3. 인증 성공 → 캐시 갱신
                cache.online = True
                cache.last_seen = datetime.now(timezone.utc)
                devices_info: list[dict] = msg.get("devices", [])
                cache.devices = {
                    d["id"]: DeviceCache(
                        id=d["id"],
                        name=d.get("name", d["id"]),
                        icon=d.get("icon", "device_unknown"),
                        connected=d.get("connected", False),
                    )
                    for d in devices_info
                }
                logger.info(
                    "[ws_manager] auth_ok: manager_id=%d devices=%s",
                    manager_id,
                    list(cache.devices.keys()),
                )

                # 4. 수신(recv) + 송신(command_queue) 동시 처리
                recv_task: asyncio.Task = asyncio.create_task(ws.recv())
                cmd_task: asyncio.Task = asyncio.create_task(cache.command_queue.get())
                try:
                    while True:
                        done, _ = await asyncio.wait(
                            {recv_task, cmd_task},
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        # 명령 큐에서 꺼낸 항목 → 기존 연결로 전송
                        if cmd_task in done:
                            cmd = cmd_task.result()
                            await ws.send(json.dumps(cmd))
                            logger.info(
                                "[ws_manager] 명령 전송: manager_id=%d cmd=%s",
                                manager_id,
                                cmd.get("command"),
                            )
                            cmd_task = asyncio.create_task(cache.command_queue.get())

                        # ss_manager로부터 수신
                        if recv_task in done:
                            raw_msg = recv_task.result()  # ConnectionClosed 시 예외 발생
                            cache.last_seen = datetime.now(timezone.utc)
                            try:
                                data = json.loads(raw_msg)
                                _handle_incoming(cache, data)
                            except json.JSONDecodeError:
                                pass
                            recv_task = asyncio.create_task(ws.recv())

                finally:
                    # 연결 종료 시 대기 중인 task 정리
                    for t in (recv_task, cmd_task):
                        if not t.done():
                            t.cancel()
                    await asyncio.gather(recv_task, cmd_task, return_exceptions=True)

        except Exception as exc:
            logger.warning(
                "[ws_manager] 연결 끊김: manager_id=%d error=%s — %ds 후 재시도",
                manager_id,
                exc,
                _RECONNECT_DELAY,
            )

        # 연결 끊김 처리
        if manager_id in _cache:
            _cache[manager_id].online = False

        await asyncio.sleep(_RECONNECT_DELAY)


async def send_command(manager_id: int, device_id: str, command: str) -> bool:
    """기존 persistent 연결을 통해 ss_manager로 명령을 전송한다.

    command_queue에 추가하면 _connect_loop가 즉시 ws.send()로 전달한다.
    오프라인이거나 캐시 없으면 False 반환.
    """
    cache = _cache.get(manager_id)
    if not cache or not cache.online:
        return False

    try:
        cache.command_queue.put_nowait(
            {"type": "command", "device_id": device_id, "command": command}
        )
        logger.info(
            "[ws_manager] 명령 큐 추가: manager_id=%d device=%s command=%s",
            manager_id,
            device_id,
            command,
        )
        return True
    except asyncio.QueueFull:
        logger.warning("[ws_manager] 명령 큐 가득 참: manager_id=%d", manager_id)
        return False


async def start_all() -> None:
    """DB에서 ss_manager 목록을 로드하고 각각 재연결 루프를 시작한다."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(SsManager))
        managers: list[SsManager] = list(result.scalars().all())

    for m in managers:
        _cache[m.id] = ManagerCache(
            manager_id=m.id,
            name=m.name,
            host=m.host,
            ws_port=m.ws_port,
            api_key=m.api_key,
        )
        task = asyncio.create_task(_connect_loop(m.id), name=f"ws_manager_{m.id}")
        _tasks[m.id] = task
        logger.info("[ws_manager] 재연결 루프 시작: manager_id=%d name=%s", m.id, m.name)

    logger.info("[ws_manager] 총 %d개 ss_manager 로드 완료", len(managers))


async def stop_all() -> None:
    """모든 재연결 루프 Task를 취소하고 완료를 대기한다."""
    for manager_id, task in _tasks.items():
        task.cancel()
        logger.info("[ws_manager] 루프 종료 요청: manager_id=%d", manager_id)
    await asyncio.gather(*_tasks.values(), return_exceptions=True)
    _tasks.clear()
    _cache.clear()
