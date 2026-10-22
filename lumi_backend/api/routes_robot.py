"""
Robot Status, Diagnostics, Battery, Location, and Map API Routes.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from lumi_backend.models.schemas import (
    BatteryStatus,
    DiagnosticsResponse,
    OccupancyMapResponse,
    Pose2D,
    RobotStatus,
)

router = APIRouter(prefix="/robot", tags=["Robot Status & Diagnostics"])


@router.get("/status", response_model=RobotStatus)
async def get_robot_status(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    db = request.app.state.db
    status = bridge.get_robot_status()
    status["unacknowledged_emergencies"] = db.count_unacknowledged_emergencies()
    return status


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def get_diagnostics(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    return bridge.get_diagnostics()


@router.get("/battery", response_model=BatteryStatus)
async def get_battery_status(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    status = bridge.get_robot_status()
    return status["battery"]


@router.get("/location", response_model=Pose2D)
async def get_robot_location(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    status = bridge.get_robot_status()
    return status["location"]


@router.get("/map", response_model=OccupancyMapResponse)
async def get_robot_map(request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    saved = db.list_destinations()
    return {
        "width": 400,
        "height": 400,
        "resolution": 0.05,
        "origin": [-10.0, -10.0, 0.0],
        "saved_destinations": saved,
        "map_image_url": "/api/v1/robot/map/image",
    }
