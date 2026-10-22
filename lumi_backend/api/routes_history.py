"""
Activity & Event History Timeline API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, Request

from lumi_backend.models.schemas import ActivityTimelineItem

router = APIRouter(prefix="/events", tags=["Activity History"])


@router.get("", response_model=List[ActivityTimelineItem])
async def list_activity_events(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    db = request.app.state.db
    return db.list_activity_logs(limit=limit, category=category)
