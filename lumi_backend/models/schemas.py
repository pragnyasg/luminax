"""
Pydantic data schemas for LUMI Caregiver REST API and WebSockets.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Pose2D(BaseModel):
    x: float = Field(0.0, description="X position in meters")
    y: float = Field(0.0, description="Y position in meters")
    theta: float = Field(0.0, description="Orientation angle in radians")
    frame_id: str = Field("map", description="Coordinate frame")


class BatteryStatus(BaseModel):
    percentage: float = Field(100.0, ge=0.0, le=100.0, description="Battery percentage")
    voltage: float = Field(12.6, description="Battery pack voltage")
    current: float = Field(0.5, description="Current draw in Amperes")
    is_charging: bool = Field(False, description="Whether robot is charging on dock")
    is_low: bool = Field(False, description="Battery low alert (< 20%)")


class RobotStatus(BaseModel):
    robot_id: str = Field("lumi-alpha-01", description="Unique robot identifier")
    name: str = Field("LUMI Healthcare Companion", description="Display name")
    is_connected: bool = Field(True, description="Live connection status to ROS 2 bridge")
    dev_mode: bool = Field(True, description="Whether operating in mock development mode")
    operating_mode: str = Field("AUTONOMOUS", description="AUTONOMOUS, MANUAL, ASSISTING, EMERGENCY_HALT")
    current_activity: str = Field("idle", description="idle, navigating, interacting, reminder, emergency, charging")
    expression: str = Field("happy", description="happy, listening, thinking, alert, sleeping, emergency")
    battery: BatteryStatus = Field(default_factory=BatteryStatus)
    location: Optional[Pose2D] = Field(default_factory=Pose2D)
    unacknowledged_emergencies: int = Field(0, description="Count of pending emergency alarms")
    next_medicine_reminder: Optional[str] = Field(None, description="Time or description of next medicine")
    last_heartbeat: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SubsystemHealth(BaseModel):
    ros2_bridge: str = "healthy"
    camera_stream: str = "healthy"
    navigation_stack: str = "healthy"
    voice_assistant: str = "healthy"
    vision_pipeline: str = "healthy"
    esp32_serial: str = "healthy"
    database: str = "healthy"


class DiagnosticsResponse(BaseModel):
    system_status: str = "operational"
    uptime_seconds: float = 3600.0
    cpu_usage_percent: float = 18.5
    memory_usage_percent: float = 42.0
    subsystems: SubsystemHealth = Field(default_factory=SubsystemHealth)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Destination(BaseModel):
    id: str
    name: str
    x: float
    y: float
    theta: float = 0.0
    description: Optional[str] = None


class OccupancyMapResponse(BaseModel):
    width: int = 400
    height: int = 400
    resolution: float = 0.05
    origin: List[float] = [-10.0, -10.0, 0.0]
    saved_destinations: List[Destination] = Field(default_factory=list)
    map_image_url: Optional[str] = "/api/v1/robot/map/image"


class NavigationGoalRequest(BaseModel):
    destination_id: Optional[str] = Field(None, description="Saved destination ID")
    x: Optional[float] = Field(None, description="Target X coordinate in map frame")
    y: Optional[float] = Field(None, description="Target Y coordinate in map frame")
    theta: float = Field(0.0, description="Target yaw angle in radians")


class NavigationGoalResponse(BaseModel):
    goal_id: str
    destination_name: str
    target_x: float
    target_y: float
    status: str = Field("ACCEPTED", description="ACCEPTED, EXECUTING, SUCCEEDED, CANCELED, FAILED")
    progress_percent: float = 0.0
    distance_remaining_m: float = 0.0
    estimated_seconds_remaining: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MedicineScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dosage: str = Field(..., min_length=1, max_length=100)
    scheduled_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM in 24hr format")
    days_of_week: List[str] = Field(
        default=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        description="List of active days",
    )
    instructions: Optional[str] = Field(None, max_length=300)


class MedicineScheduleUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    scheduled_time: Optional[str] = None
    days_of_week: Optional[List[str]] = None
    instructions: Optional[str] = None
    is_active: Optional[bool] = None


class MedicineSchedule(BaseModel):
    id: str
    name: str
    dosage: str
    scheduled_time: str
    days_of_week: List[str]
    instructions: Optional[str] = None
    is_active: bool = True
    created_at: str


class MedicineLogEntry(BaseModel):
    id: str
    medicine_id: str
    medicine_name: str
    dosage: str
    scheduled_time: str
    status: str = Field("pending", description="pending, spoken, taken, skipped, missed")
    confirmed_by: Optional[str] = None
    confirmed_at: Optional[str] = None
    notes: Optional[str] = None


class MedicineActionRequest(BaseModel):
    action: str = Field("taken", description="taken, skipped, or acknowledge")
    confirmed_by: str = Field("caregiver", min_length=1)
    notes: Optional[str] = None


class AdherenceSummary(BaseModel):
    total_doses: int = 0
    taken_count: int = 0
    skipped_count: int = 0
    missed_count: int = 0
    adherence_rate_percent: float = 100.0


class EmergencyEvent(BaseModel):
    event_id: str
    event_type: str = Field("fall_confirmed", description="fall_confirmed, fall_suspected, medicine_unacknowledged")
    severity: str = Field("CRITICAL", description="LOW, MEDIUM, HIGH, CRITICAL")
    timestamp: str
    confidence: float = 0.95
    person_name: Optional[str] = "Primary Patient"
    posture: str = "lying_down"
    location: Optional[Pose2D] = None
    snapshot_url: Optional[str] = None
    acknowledged: bool = False
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolution_notes: Optional[str] = None


class AcknowledgeEmergencyRequest(BaseModel):
    acknowledged_by: str = Field("caregiver", min_length=1, max_length=100)
    note: Optional[str] = Field(None, max_length=500)


class EmergencyCallRequest(BaseModel):
    responder_phone: Optional[str] = None
    note: Optional[str] = None


class ManualControlCommand(BaseModel):
    linear_x: float = Field(0.0, ge=-0.4, le=0.4, description="Linear velocity in m/s")
    angular_z: float = Field(0.0, ge=-1.0, le=1.0, description="Angular velocity in rad/s")
    enable_safety_override: bool = Field(False, description="Requires special safety state")


class VoiceCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=500)


class VoiceInteraction(BaseModel):
    id: str
    timestamp: str
    recognized_speech: str
    response_text: str
    speaker: str = "LUMI"
    source: str = "voice_node"


class AudioDevice(BaseModel):
    id: int
    name: str
    device_type: str = Field("output", description="input or output")
    is_default: bool = False


class AudioTestRequest(BaseModel):
    phrase: str = "Hello, this is LUMI voice assistant testing the audio speaker."
    device_id: Optional[int] = None


class PersonTrack(BaseModel):
    track_id: int
    person_name: Optional[str] = "Primary Patient"
    confidence: float = 0.92
    posture: str = "standing"
    presence_state: str = "PRESENT"
    last_seen_timestamp: str
    bbox: Optional[List[int]] = None


class ActivityTimelineItem(BaseModel):
    id: str
    timestamp: str
    category: str = Field("system", description="medicine, emergency, navigation, voice, system, presence")
    severity: str = Field("INFO", description="INFO, WARNING, ALERT, CRITICAL")
    title: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WebSocketEvent(BaseModel):
    type: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Dict[str, Any] = Field(default_factory=dict)
