"""Materials API — oxide list and future material navigation endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from mat_nav_lib import get_oxides

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/oxides")
async def list_oxides(category: str | None = None):
    """Return the full oxide list, optionally filtered by category."""
    return get_oxides(category=category)
