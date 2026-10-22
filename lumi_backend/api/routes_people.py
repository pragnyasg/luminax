"""
People & Activity Monitoring API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Request

from lumi_backend.models.schemas import PersonTrack

router = APIRouter(prefix="/people", tags=["People & Activity Monitoring"])


@router.get("", response_model=List[PersonTrack])
async def list_people_and_activities(request: Request) -> List[Dict[str, Any]]:
    bridge = request.app.state.bridge
    return bridge.get_person_tracks()
