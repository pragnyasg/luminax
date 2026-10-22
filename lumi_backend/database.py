"""
SQLite Database Layer for LUMI Caregiver Backend.
Durable persistence for medicine schedules, logs, emergency history, and activity timeline.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        self._seed_default_data()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Medicine schedules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicine_schedules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    days_of_week TEXT NOT NULL,
                    instructions TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

            # 2. Medicine adherence logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicine_logs (
                    id TEXT PRIMARY KEY,
                    medicine_id TEXT NOT NULL,
                    medicine_name TEXT NOT NULL,
                    dosage TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confirmed_by TEXT,
                    confirmed_at TEXT,
                    notes TEXT,
                    FOREIGN KEY (medicine_id) REFERENCES medicine_schedules(id)
                )
            """)

            # 3. Emergency events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emergency_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    person_name TEXT,
                    posture TEXT,
                    location_json TEXT,
                    snapshot_url TEXT,
                    acknowledged INTEGER NOT NULL DEFAULT 0,
                    acknowledged_at TEXT,
                    acknowledged_by TEXT,
                    resolution_notes TEXT
                )
            """)

            # 4. Activity timeline table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)

            # 5. Saved navigation destinations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_destinations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    theta REAL NOT NULL DEFAULT 0.0,
                    description TEXT
                )
            """)

            # 6. Caregiver settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS caregiver_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            conn.commit()

    def _seed_default_data(self) -> None:
        """Seed realistic initial destinations, sample medicine, and activity logs if empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Seed destinations if empty
            cursor.execute("SELECT COUNT(*) FROM saved_destinations")
            if cursor.fetchone()[0] == 0:
                default_destinations = [
                    ("dest-living-room", "Living Room", 2.5, 1.2, 0.0, "Central living and seating area"),
                    ("dest-bedroom", "Bedroom", -1.8, 3.4, 1.57, "Patient bedroom beside bedside table"),
                    ("dest-kitchen", "Kitchen", 3.2, -2.1, -1.57, "Kitchen medicine cabinet counter"),
                    ("dest-medicine-station", "Medicine Station", 0.5, 2.0, 0.78, "Designated healthcare supply station"),
                    ("dest-charging-dock", "Charging Dock", 0.0, 0.0, 0.0, "Base home charging dock"),
                ]
                cursor.executemany(
                    "INSERT INTO saved_destinations (id, name, x, y, theta, description) VALUES (?, ?, ?, ?, ?, ?)",
                    default_destinations,
                )

            # Seed sample medicine schedule if empty
            cursor.execute("SELECT COUNT(*) FROM medicine_schedules")
            if cursor.fetchone()[0] == 0:
                now_str = datetime.now(timezone.utc).isoformat()
                default_meds = [
                    (
                        "med-01",
                        "Amlodipine (Blood Pressure)",
                        "5 mg - 1 tablet",
                        "08:00",
                        json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                        "Take in morning with a full glass of water.",
                        1,
                        now_str,
                    ),
                    (
                        "med-02",
                        "Metformin (Blood Sugar)",
                        "500 mg - 1 tablet",
                        "13:00",
                        json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                        "Take immediately with lunch meal.",
                        1,
                        now_str,
                    ),
                    (
                        "med-03",
                        "Atorvastatin (Cholesterol)",
                        "20 mg - 1 tablet",
                        "20:00",
                        json.dumps(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
                        "Take in evening before bedtime.",
                        1,
                        now_str,
                    ),
                ]
                cursor.executemany(
                    "INSERT INTO medicine_schedules (id, name, dosage, scheduled_time, days_of_week, instructions, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    default_meds,
                )

            # Seed sample activity log if empty
            cursor.execute("SELECT COUNT(*) FROM activity_logs")
            if cursor.fetchone()[0] == 0:
                now_str = datetime.now(timezone.utc).isoformat()
                logs = [
                    (
                        str(uuid.uuid4()),
                        now_str,
                        "system",
                        "INFO",
                        "System Initialized",
                        "LUMI Healthcare Companion online and ready for monitoring.",
                        json.dumps({"subsystem": "supervisor"}),
                    ),
                    (
                        str(uuid.uuid4()),
                        now_str,
                        "medicine",
                        "INFO",
                        "Schedule Loaded",
                        "3 daily medicine schedules active.",
                        json.dumps({"count": 3}),
                    ),
                ]
                cursor.executemany(
                    "INSERT INTO activity_logs (id, timestamp, category, severity, title, description, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    logs,
                )

            conn.commit()

    # -----------------------------------------------------------------------
    # Medicine Schedules Methods
    # -----------------------------------------------------------------------
    def list_medicine_schedules(self, active_only: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if active_only:
                cursor.execute("SELECT * FROM medicine_schedules WHERE is_active = 1 ORDER BY scheduled_time ASC")
            else:
                cursor.execute("SELECT * FROM medicine_schedules ORDER BY scheduled_time ASC")
            rows = cursor.fetchall()

            result = []
            for r in rows:
                item = dict(r)
                item["days_of_week"] = json.loads(item["days_of_week"])
                item["is_active"] = bool(item["is_active"])
                result.append(item)
            return result

    def get_medicine_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicine_schedules WHERE id = ?", (schedule_id,))
            r = cursor.fetchone()
            if not r:
                return None
            item = dict(r)
            item["days_of_week"] = json.loads(item["days_of_week"])
            item["is_active"] = bool(item["is_active"])
            return item

    def create_medicine_schedule(
        self,
        name: str,
        dosage: str,
        scheduled_time: str,
        days_of_week: List[str],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        schedule_id = f"med-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO medicine_schedules (id, name, dosage, scheduled_time, days_of_week, instructions, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (schedule_id, name, dosage, scheduled_time, json.dumps(days_of_week), instructions, created_at),
            )
            conn.commit()

        self.add_activity_log(
            category="medicine",
            severity="INFO",
            title="Medicine Added",
            description=f"Scheduled {name} ({dosage}) at {scheduled_time}",
            metadata={"schedule_id": schedule_id},
        )
        return self.get_medicine_schedule(schedule_id)  # type: ignore

    def update_medicine_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = self.get_medicine_schedule(schedule_id)
        if not existing:
            return None

        fields = []
        values = []
        for k, v in updates.items():
            if v is not None:
                if k == "days_of_week":
                    fields.append(f"{k} = ?")
                    values.append(json.dumps(v))
                elif k == "is_active":
                    fields.append(f"{k} = ?")
                    values.append(1 if v else 0)
                else:
                    fields.append(f"{k} = ?")
                    values.append(v)

        if not fields:
            return existing

        values.append(schedule_id)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE medicine_schedules SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

        return self.get_medicine_schedule(schedule_id)

    def delete_medicine_schedule(self, schedule_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicine_schedules WHERE id = ?", (schedule_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    # -----------------------------------------------------------------------
    # Medicine Logs & Adherence
    # -----------------------------------------------------------------------
    def record_medicine_log(
        self,
        medicine_id: str,
        medicine_name: str,
        dosage: str,
        scheduled_time: str,
        status: str,
        confirmed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        log_id = f"log-{uuid.uuid4().hex[:8]}"
        confirmed_at = datetime.now(timezone.utc).isoformat() if status in ("taken", "skipped") else None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO medicine_logs (id, medicine_id, medicine_name, dosage, scheduled_time, status, confirmed_by, confirmed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, medicine_id, medicine_name, dosage, scheduled_time, status, confirmed_by, confirmed_at, notes),
            )
            conn.commit()

        return {
            "id": log_id,
            "medicine_id": medicine_id,
            "medicine_name": medicine_name,
            "dosage": dosage,
            "scheduled_time": scheduled_time,
            "status": status,
            "confirmed_by": confirmed_by,
            "confirmed_at": confirmed_at,
            "notes": notes,
        }

    def list_medicine_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicine_logs ORDER BY rowid DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_adherence_summary(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM medicine_logs GROUP BY status")
            counts = {row[0]: row[1] for row in cursor.fetchall()}

            taken = counts.get("taken", 0)
            skipped = counts.get("skipped", 0)
            missed = counts.get("missed", 0)
            total = taken + skipped + missed
            rate = round((taken / total * 100.0), 1) if total > 0 else 100.0

            return {
                "total_doses": total,
                "taken_count": taken,
                "skipped_count": skipped,
                "missed_count": missed,
                "adherence_rate_percent": rate,
            }

    # -----------------------------------------------------------------------
    # Emergency Events
    # -----------------------------------------------------------------------
    def record_emergency_event(
        self,
        event_type: str,
        severity: str,
        confidence: float,
        posture: str,
        person_name: Optional[str] = "Primary Patient",
        location: Optional[Dict[str, Any]] = None,
        snapshot_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        event_id = f"em-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now(timezone.utc).isoformat()
        loc_str = json.dumps(location) if location else None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO emergency_events (
                    event_id, event_type, severity, timestamp, confidence, person_name,
                    posture, location_json, snapshot_url, acknowledged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (event_id, event_type, severity, now_str, confidence, person_name, posture, loc_str, snapshot_url),
            )
            conn.commit()

        self.add_activity_log(
            category="emergency",
            severity="CRITICAL" if severity == "CRITICAL" else "ALERT",
            title=f"Emergency Alert: {event_type.replace('_', ' ').title()}",
            description=f"Detected with {int(confidence*100)}% confidence. Posture: {posture}",
            metadata={"event_id": event_id, "severity": severity},
        )

        return self.get_emergency_event(event_id)  # type: ignore

    def get_emergency_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emergency_events WHERE event_id = ?", (event_id,))
            r = cursor.fetchone()
            if not r:
                return None
            item = dict(r)
            item["acknowledged"] = bool(item["acknowledged"])
            item["location"] = json.loads(item["location_json"]) if item["location_json"] else None
            del item["location_json"]
            return item

    def list_emergency_events(self, limit: int = 50, unacknowledged_only: bool = False) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if unacknowledged_only:
                cursor.execute(
                    "SELECT * FROM emergency_events WHERE acknowledged = 0 ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            else:
                cursor.execute("SELECT * FROM emergency_events ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["acknowledged"] = bool(item["acknowledged"])
                item["location"] = json.loads(item["location_json"]) if item["location_json"] else None
                del item["location_json"]
                result.append(item)
            return result

    def acknowledge_emergency(self, event_id: str, acknowledged_by: str = "caregiver", note: Optional[str] = None) -> bool:
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE emergency_events
                SET acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?, resolution_notes = ?
                WHERE event_id = ?
                """,
                (now_str, acknowledged_by, note, event_id),
            )
            updated = cursor.rowcount > 0
            conn.commit()

        if updated:
            self.add_activity_log(
                category="emergency",
                severity="INFO",
                title="Emergency Acknowledged",
                description=f"Alert {event_id} acknowledged by {acknowledged_by}.",
                metadata={"event_id": event_id, "note": note},
            )
        return updated

    def count_unacknowledged_emergencies(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM emergency_events WHERE acknowledged = 0")
            return cursor.fetchone()[0]

    # -----------------------------------------------------------------------
    # Activity Timeline Logs
    # -----------------------------------------------------------------------
    def add_activity_log(
        self,
        category: str,
        severity: str,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        log_id = f"act-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO activity_logs (id, timestamp, category, severity, title, description, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (log_id, now_str, category, severity, title, description, json.dumps(metadata or {})),
            )
            conn.commit()

        return {
            "id": log_id,
            "timestamp": now_str,
            "category": category,
            "severity": severity,
            "title": title,
            "description": description,
            "metadata": metadata or {},
        }

    def list_activity_logs(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT * FROM activity_logs WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                    (category, limit),
                )
            else:
                cursor.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["metadata"] = json.loads(item["metadata_json"]) if item["metadata_json"] else {}
                del item["metadata_json"]
                result.append(item)
            return result

    # -----------------------------------------------------------------------
    # Destinations
    # -----------------------------------------------------------------------
    def list_destinations(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM saved_destinations ORDER BY name ASC")
            return [dict(r) for r in cursor.fetchall()]

    def get_destination(self, dest_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM saved_destinations WHERE id = ?", (dest_id,))
            r = cursor.fetchone()
            return dict(r) if r else None
