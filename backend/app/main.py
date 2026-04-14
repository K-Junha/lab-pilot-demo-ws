"""LAB Pilot Backend — FastAPI 진입점"""
from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.devices import router as devices_router, _executor as devices_executor
from app.api.materials import router as materials_router
from app.api.ws import router as ws_router, _ws_executor


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # clean shutdown: 진행 중인 작업 완료 후 executor 종료
    devices_executor.shutdown(wait=False)
    _ws_executor.shutdown(wait=False)


app = FastAPI(title="LAB Pilot Backend", version="0.1.0", lifespan=lifespan)

# 개발 환경: 로컬 프론트엔드 origin만 허용
# 프로덕션에서는 실제 도메인으로 교체할 것
ALLOWED_ORIGINS = [
    "http://localhost:9000",
    "http://localhost:9001",
    "http://localhost:9002",
    "http://localhost:9003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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
