"""
Manual Robot Teleoperation & Safety Control API Routes.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request, status

from lumi_backend.config import settings
from lumi_backend.models.schemas import ManualControlCommand

router = APIRouter(prefix="/control", tags=["Manual Robot Control"])


@router.post("/manual")
async def send_manual_control(cmd: ManualControlCommand, request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    robot_status = bridge.get_robot_status()

    # Safety interlock check: Cannot drive in EMERGENCY_HALT mode without override
    if robot_status.get("operating_mode") == "EMERGENCY_HALT" and not cmd.enable_safety_override:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Movement blocked: Robot is in EMERGENCY_HALT state. Clear emergency or enable safety override.",
        )

    success = bridge.send_cmd_vel(linear_x=cmd.linear_x, angular_z=cmd.angular_z)
    return {
        "success": success,
        "linear_x": cmd.linear_x,
        "angular_z": cmd.angular_z,
        "speed_limits": {
            "max_linear": settings.max_linear_speed,
            "max_angular": settings.max_angular_speed,
        },
    }


@router.post("/stop")
async def stop_robot_motion(request: Request) -> Dict[str, Any]:
    bridge = request.app.state.bridge
    db = request.app.state.db

    success = bridge.stop_robot()
    db.add_activity_log(
        category="system",
        severity="WARNING",
        title="Robot Motion Stopped",
        description="Caregiver initiated immediate motion stop.",
    )
    return {"success": success, "message": "Emergency motion stop executed"}
