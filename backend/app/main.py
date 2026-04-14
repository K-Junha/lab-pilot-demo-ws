"""LAB Pilot Backend — FastAPI 진입점"""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.devices import router as devices_router
from app.api.materials import router as materials_router
from app.api.ws import router as ws_router

app = FastAPI(title="LAB Pilot Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
