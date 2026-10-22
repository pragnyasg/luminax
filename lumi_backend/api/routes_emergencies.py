"""
Emergency & Fall Detection Management API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query, Request, status

from lumi_backend.api.websocket import ws_manager
from lumi_backend.config import settings
from lumi_backend.models.schemas import (
    AcknowledgeEmergencyRequest,
    EmergencyCallRequest,
    EmergencyEvent,
)

router = APIRouter(prefix="/emergencies", tags=["Emergency & Fall Detection"])


@router.get("", response_model=List[EmergencyEvent])
async def list_emergencies(
    request: Request,
    unacknowledged_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=500),
) -> List[Dict[str, Any]]:
    db = request.app.state.db
    return db.list_emergency_events(limit=limit, unacknowledged_only=unacknowledged_only)


@router.get("/{event_id}", response_model=EmergencyEvent)
async def get_emergency(event_id: str, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    ev = db.get_emergency_event(event_id)
    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency event '{event_id}' not found",
        )
    return ev


@router.post("/{event_id}/acknowledge")
async def acknowledge_emergency(
    event_id: str,
    req: AcknowledgeEmergencyRequest,
    request: Request,
) -> Dict[str, Any]:
    db = request.app.state.db
    bridge = request.app.state.bridge

    success = db.acknowledge_emergency(
        event_id=event_id,
        acknowledged_by=req.acknowledged_by,
        note=req.note,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency event '{event_id}' not found",
        )

    ev = db.get_emergency_event(event_id)
    # Broadcast acknowledgment across WebSockets
    await ws_manager.broadcast({
        "type": "emergency.acknowledged",
        "event_id": event_id,
        "acknowledged_by": req.acknowledged_by,
        "note": req.note,
    })

    # Command robot to speak confirmation
    bridge.speak_phrase("Emergency acknowledged by caregiver. Assistance is coordinated.")

    return {
        "success": True,
        "event_id": event_id,
        "acknowledged_by": req.acknowledged_by,
        "event": ev,
    }


@router.post("/{event_id}/call")
async def call_emergency_responder(
    event_id: str,
    req: EmergencyCallRequest,
    request: Request,
) -> Dict[str, Any]:
    db = request.app.state.db
    ev = db.get_emergency_event(event_id)
    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency event '{event_id}' not found",
        )

    phone = req.responder_phone or settings.emergency_contact_phone
    db.add_activity_log(
        category="emergency",
        severity="ALERT",
        title="Emergency Call Dispatched",
        description=f"Direct call initiated to responder {phone} for event {event_id}.",
        metadata={"event_id": event_id, "phone": phone, "note": req.note},
    )

    return {
        "success": True,
        "event_id": event_id,
        "responder_phone": phone,
        "status": "call_initiated",
        "message": f"Emergency call routed to {phone}",
    }


@router.post("/simulate_fall", response_model=EmergencyEvent)
async def simulate_fall_event(request: Request) -> Dict[str, Any]:
    """Test helper route to generate a realistic fall detection alarm."""
    db = request.app.state.db
    bridge = request.app.state.bridge
    notification_mgr = request.app.state.notification_mgr

    # Record emergency event
    ev = db.record_emergency_event(
        event_type="fall_confirmed",
        severity="CRITICAL",
        confidence=0.96,
        posture="lying_down",
        person_name="Primary Patient",
        location=bridge.get_robot_status().get("location"),
        snapshot_url="/api/v1/camera/snapshot",
    )

    # Spoken alert on robot
    bridge.speak_phrase("Warning! Fall detected. Asking if patient is okay. Alerting caregiver.")

    # Send caregiver notification
    notification_mgr.notify_emergency(
        title="CRITICAL FALL ALERT",
        message="LUMI detected patient fall in living area with 96% confidence.",
        event_data=ev,
    )

    # Real-time WebSocket broadcast
    await ws_manager.broadcast({
        "type": "vision.fall_detected",
        "event": ev,
    })

    return ev
