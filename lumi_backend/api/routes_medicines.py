"""
Medicine Schedule Management, Adherence Logging, and Reminder API Routes.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query, Request, status

from lumi_backend.models.schemas import (
    AdherenceSummary,
    MedicineActionRequest,
    MedicineLogEntry,
    MedicineSchedule,
    MedicineScheduleCreate,
    MedicineScheduleUpdate,
)

router = APIRouter(prefix="/medicines", tags=["Medicine Management"])


@router.get("", response_model=List[MedicineSchedule])
async def list_medicines(request: Request, active_only: bool = Query(False)) -> List[Dict[str, Any]]:
    db = request.app.state.db
    return db.list_medicine_schedules(active_only=active_only)


@router.post("", response_model=MedicineSchedule, status_code=status.HTTP_201_CREATED)
async def create_medicine(req: MedicineScheduleCreate, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    return db.create_medicine_schedule(
        name=req.name,
        dosage=req.dosage,
        scheduled_time=req.scheduled_time,
        days_of_week=req.days_of_week,
        instructions=req.instructions,
    )


@router.get("/{schedule_id}", response_model=MedicineSchedule)
async def get_medicine(schedule_id: str, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    med = db.get_medicine_schedule(schedule_id)
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine schedule '{schedule_id}' not found",
        )
    return med


@router.patch("/{schedule_id}", response_model=MedicineSchedule)
async def update_medicine(schedule_id: str, req: MedicineScheduleUpdate, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    updates = req.model_dump(exclude_unset=True)
    updated = db.update_medicine_schedule(schedule_id, updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine schedule '{schedule_id}' not found",
        )
    return updated


@router.delete("/{schedule_id}")
async def delete_medicine(schedule_id: str, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    success = db.delete_medicine_schedule(schedule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine schedule '{schedule_id}' not found",
        )
    return {"success": True, "message": f"Medicine schedule '{schedule_id}' deleted"}


@router.post("/{schedule_id}/trigger", response_model=MedicineLogEntry)
async def trigger_medicine_reminder(schedule_id: str, request: Request) -> Dict[str, Any]:
    med_service = request.app.state.med_service
    log_entry = med_service.trigger_reminder(schedule_id)
    if not log_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine schedule '{schedule_id}' not found",
        )
    return log_entry


@router.post("/{schedule_id}/action")
async def record_medicine_action(schedule_id: str, req: MedicineActionRequest, request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    med_service = request.app.state.med_service

    med = db.get_medicine_schedule(schedule_id)
    if not med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine schedule '{schedule_id}' not found",
        )

    med_service.acknowledge_reminder(
        action=req.action,
        confirmed_by=req.confirmed_by,
        notes=req.notes,
    )

    log_entry = db.record_medicine_log(
        medicine_id=med["id"],
        medicine_name=med["name"],
        dosage=med["dosage"],
        scheduled_time=med["scheduled_time"],
        status=req.action,
        confirmed_by=req.confirmed_by,
        notes=req.notes,
    )

    db.add_activity_log(
        category="medicine",
        severity="INFO",
        title=f"Medicine {req.action.capitalize()}",
        description=f"{med['name']} marked as {req.action} by {req.confirmed_by}.",
        metadata={"medicine_id": schedule_id, "action": req.action},
    )

    return {"success": True, "log_entry": log_entry}


@router.get("/logs/history", response_model=List[MedicineLogEntry])
async def list_medicine_logs(request: Request, limit: int = Query(50, ge=1, le=500)) -> List[Dict[str, Any]]:
    db = request.app.state.db
    return db.list_medicine_logs(limit=limit)


@router.get("/adherence/summary", response_model=AdherenceSummary)
async def get_adherence_summary(request: Request) -> Dict[str, Any]:
    db = request.app.state.db
    return db.get_adherence_summary()
