"""LAB Pilot Backend — FastAPI 진입점"""
from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

# Windows에서 asyncpg는 SelectorEventLoop 필요
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.auth import router as auth_router
from app.api.workflows import router as workflows_router
from app.api.logs import router as logs_router
from app.api.results import router as results_router
from app.api.admin import router as admin_router
from app.api.devices import router as devices_router, _executor as devices_executor, start_watchdog, stop_watchdog
from app.api.materials import router as materials_router
from app.api.ws import router as ws_router
from app.api.ws_manager_client import start_all as start_manager_clients, stop_all as stop_manager_clients
from app.core.logger import purge_old_logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    purge_old_logs()
    await start_watchdog()
    await start_manager_clients()
    yield
    await stop_manager_clients()
    await stop_watchdog()
    devices_executor.shutdown(wait=False)


app = FastAPI(title="LAB Pilot Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(workflows_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(results_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(devices_router, prefix="/api")
app.include_router(materials_router, prefix="/api")
app.include_router(ws_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


def run():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
