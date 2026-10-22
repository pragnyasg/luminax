"""
Indoor Navigation and Saved Destination API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Request, status

from lumi_backend.models.schemas import (
    Destination,
    NavigationGoalRequest,
    NavigationGoalResponse,
)

router = APIRouter(prefix="/navigation", tags=["Indoor Navigation"])


@router.get("/destinations", response_model=List[Destination])
async def list_destinations(request: Request) -> List[Dict[str, Any]]:
    db = request.app.state.db
    return db.list_destinations()


@router.get("/goals", response_model=NavigationGoalResponse)
async def get_current_goal(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    return bridge.get_navigation_status()


@router.post("/goals", response_model=NavigationGoalResponse)
async def dispatch_goal(req: NavigationGoalRequest, request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    db = request.app.state.db

    target_x = req.x
    target_y = req.y
    target_theta = req.theta
    dest_name = "Custom Coordinate"

    if req.destination_id:
        dest = db.get_destination(req.destination_id)
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination '{req.destination_id}' not found",
            )
        target_x = dest["x"]
        target_y = dest["y"]
        target_theta = dest["theta"]
        dest_name = dest["name"]

    if target_x is None or target_y is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either destination_id or x, y coordinates",
        )

    goal_resp = bridge.navigate_to_pose(target_x, target_y, target_theta, destination_name=dest_name)
    db.add_activity_log(
        category="navigation",
        severity="INFO",
        title="Navigation Goal Dispatched",
        description=f"Robot dispatched to {dest_name} ({target_x:.1f}, {target_y:.1f})",
        metadata={"goal_id": goal_resp.get("goal_id")},
    )
    return goal_resp


@router.post("/cancel")
async def cancel_goal(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    db = request.app.state.db
    canceled = bridge.cancel_navigation()
    db.add_activity_log(
        category="navigation",
        severity="WARNING",
        title="Navigation Canceled",
        description="Active navigation goal canceled by caregiver.",
    )
    return {"success": canceled, "message": "Navigation goal canceled" if canceled else "No active goal to cancel"}
