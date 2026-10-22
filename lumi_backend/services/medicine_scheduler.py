"""
Authoritative Medicine Scheduler Service.
Tracks active schedules, dispatches robot reminder prompts, monitors patient acknowledgment,
and escalates unacknowledged doses to caregiver emergency alarms.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from lumi_backend.config import settings
from lumi_backend.database import Database
from lumi_backend.ros2_bridge.bridge_interface import RobotBridgeBase

logger = logging.getLogger(__name__)


class MedicineSchedulerService:
    def __init__(self, db: Database, bridge: RobotBridgeBase) -> None:
        self.db = db
        self.bridge = bridge
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._pending_reminders: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True, name="LumiMedScheduler")
        self._thread.start()
        logger.info("Medicine Scheduler Service started.")

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Medicine Scheduler Service stopped.")

    def _run_scheduler(self) -> None:
        """1 Hz Scheduler Loop checking due medicines and escalation timers."""
        last_checked_minute: Optional[str] = None

        while self._running:
            now = datetime.now()
            current_time_str = now.strftime("%H:%M")
            day_name = now.strftime("%a")  # e.g. "Mon"

            # Check for due medicines once per minute
            if current_time_str != last_checked_minute:
                last_checked_minute = current_time_str
                self._check_due_medicines(current_time_str, day_name)

            # Check for escalations on unacknowledged reminders
            self._check_escalations()

            time.sleep(1.0)

    def _check_due_medicines(self, time_str: str, day_name: str) -> None:
        schedules = self.db.list_medicine_schedules(active_only=True)
        for s in schedules:
            if s["scheduled_time"] == time_str and day_name in s["days_of_week"]:
                self.trigger_reminder(s["id"])

    def trigger_reminder(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Fires a medicine reminder immediately."""
        schedule = self.db.get_medicine_schedule(schedule_id)
        if not schedule:
            return None

        # 1. Trigger spoken alert on robot
        self.bridge.trigger_medicine_reminder(schedule["name"], schedule["dosage"])

        # 2. Record pending log
        log_entry = self.db.record_medicine_log(
            medicine_id=schedule["id"],
            medicine_name=schedule["name"],
            dosage=schedule["dosage"],
            scheduled_time=schedule["scheduled_time"],
            status="spoken",
            notes=f"Reminder spoken by LUMI: {schedule.get('instructions') or ''}",
        )

        with self._lock:
            self._pending_reminders[log_entry["id"]] = {
                "log_id": log_entry["id"],
                "schedule": schedule,
                "triggered_at": time.time(),
                "escalated": False,
            }

        logger.info(f"Triggered medicine reminder for '{schedule['name']}' ({schedule['dosage']})")
        return log_entry

    def _check_escalations(self) -> None:
        now = time.time()
        timeout = settings.medicine_escalation_sec

        with self._lock:
            for log_id, info in list(self._pending_reminders.items()):
                if not info["escalated"] and (now - info["triggered_at"]) >= timeout:
                    info["escalated"] = True
                    schedule = info["schedule"]

                    # Escalate to emergency alert in database
                    self.db.record_emergency_event(
                        event_type="medicine_unacknowledged",
                        severity="HIGH",
                        confidence=1.0,
                        posture="unknown",
                        person_name="Primary Patient",
                        location=self.bridge.get_robot_status().get("location"),
                    )

                    # Prompt robot to escalate speech
                    self.bridge.speak_phrase(
                        f"Warning! Medicine reminder for {schedule['name']} has not been confirmed. Notifying caregiver."
                    )

                    # Update log status to missed
                    self.db.record_medicine_log(
                        medicine_id=schedule["id"],
                        medicine_name=schedule["name"],
                        dosage=schedule["dosage"],
                        scheduled_time=schedule["scheduled_time"],
                        status="missed",
                        notes=f"Unacknowledged after {int(timeout)} seconds. Caregiver alerted.",
                    )
                    logger.warn(f"Medicine reminder for {schedule['name']} escalated to caregiver alert!")

    def acknowledge_reminder(
        self,
        log_id: Optional[str] = None,
        action: str = "taken",
        confirmed_by: str = "caregiver",
        notes: Optional[str] = None,
    ) -> bool:
        """Confirms a medicine was taken or skipped."""
        self.bridge.acknowledge_medicine_reminder()

        with self._lock:
            if log_id and log_id in self._pending_reminders:
                info = self._pending_reminders.pop(log_id)
                schedule = info["schedule"]
                self.db.record_medicine_log(
                    medicine_id=schedule["id"],
                    medicine_name=schedule["name"],
                    dosage=schedule["dosage"],
                    scheduled_time=schedule["scheduled_time"],
                    status=action,
                    confirmed_by=confirmed_by,
                    notes=notes or f"Confirmed by {confirmed_by}",
                )
                return True
            elif self._pending_reminders:
                # Acknowledge most recent pending reminder
                first_key = next(iter(self._pending_reminders))
                info = self._pending_reminders.pop(first_key)
                schedule = info["schedule"]
                self.db.record_medicine_log(
                    medicine_id=schedule["id"],
                    medicine_name=schedule["name"],
                    dosage=schedule["dosage"],
                    scheduled_time=schedule["scheduled_time"],
                    status=action,
                    confirmed_by=confirmed_by,
                    notes=notes or f"Confirmed by {confirmed_by}",
                )
                return True
            else:
                # No active pending reminder, but log manual confirmation
                return True
