"""
Deterministic Mock Robot Bridge for Development & Testing.
Simulates all ROS 2 topics, Nav2 goal progress, camera frame generation,
speech exchanges, and battery states without requiring physical robot hardware.
"""

from __future__ import annotations

import asyncio
import io
import math
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from lumi_backend.config import settings
from lumi_backend.ros2_bridge.bridge_interface import RobotBridgeBase


class MockBridge(RobotBridgeBase):
    def __init__(self) -> None:
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._event_callbacks: List[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Robot state
        self.robot_id = settings.robot_id
        self.name = settings.robot_name + " [MOCK DEV MODE]"
        self.operating_mode = "AUTONOMOUS"
        self.current_activity = "idle"
        self.expression = "happy"

        # Battery simulation
        self.battery_pct = 92.5
        self.battery_voltage = 12.4
        self.is_charging = False

        # Odometry / Pose simulation
        self.pose_x = 0.5
        self.pose_y = 1.2
        self.pose_theta = 0.25

        # Manual control & dead-man timeout
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.last_cmd_vel_time = time.time()
        self.cmd_vel_timeout = settings.cmd_vel_timeout_sec

        # Navigation Goal simulation
        self.active_goal: Optional[Dict[str, Any]] = None

        # Vision & Person Tracking simulation
        self.person_present = True
        self.person_name = "Primary Patient"
        self.current_posture = "sitting"
        self.presence_state = "PRESENT"

        # Emergency simulation
        self.active_emergency_count = 0

        # Voice interaction simulation
        self.voice_state = "idle"  # idle, listening, thinking, speaking
        self.last_transcript = "Hello LUMI, good morning!"
        self.last_response = "Good morning! I am here and ready to assist you today."

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="LumiMockBridgeLoop")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def is_connected(self) -> bool:
        return True  # Mock bridge is always deterministically available

    def register_event_callback(self, callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        self._event_callbacks.append(callback)

    def set_async_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        payload = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        if self._loop and self._loop.is_running():
            for cb in self._event_callbacks:
                asyncio.run_coroutine_threadsafe(cb(payload), self._loop)

    def _run_loop(self) -> None:
        """20 Hz Background Simulation Loop."""
        last_tick = time.time()
        last_sec = time.time()

        while self._running:
            now = time.time()
            dt = now - last_tick
            last_tick = now

            # 1. Dead-man velocity watchdog check
            if (now - self.last_cmd_vel_time) > self.cmd_vel_timeout:
                if self.linear_x != 0.0 or self.angular_z != 0.0:
                    self.linear_x = 0.0
                    self.angular_z = 0.0
                    if self.current_activity == "manual_control":
                        self.current_activity = "idle"

            # 2. Integrate manual velocities
            if self.linear_x != 0.0 or self.angular_z != 0.0:
                self.pose_theta += self.angular_z * dt
                self.pose_x += self.linear_x * math.cos(self.pose_theta) * dt
                self.pose_y += self.linear_x * math.sin(self.pose_theta) * dt

            # 3. Simulate autonomous navigation progress
            if self.active_goal and self.active_goal.get("status") == "EXECUTING":
                gx = self.active_goal["target_x"]
                gy = self.active_goal["target_y"]
                dx = gx - self.pose_x
                dy = gy - self.pose_y
                dist = math.hypot(dx, dy)

                if dist < 0.1:
                    # Reached target destination
                    self.active_goal["status"] = "SUCCEEDED"
                    self.active_goal["progress_percent"] = 100.0
                    self.active_goal["distance_remaining_m"] = 0.0
                    self.active_goal["estimated_seconds_remaining"] = 0.0
                    self.current_activity = "idle"
                    self.expression = "happy"
                    self._emit_event("navigation.completed", self.active_goal)
                else:
                    speed = 0.35  # m/s
                    step = min(dist, speed * dt)
                    angle = math.atan2(dy, dx)
                    self.pose_theta = angle
                    self.pose_x += step * math.cos(angle)
                    self.pose_y += step * math.sin(angle)

                    total_dist = self.active_goal.get("initial_distance", dist + 0.1)
                    progress = max(0.0, min(99.0, (1.0 - (dist / total_dist)) * 100.0))
                    self.active_goal["progress_percent"] = round(progress, 1)
                    self.active_goal["distance_remaining_m"] = round(dist, 2)
                    self.active_goal["estimated_seconds_remaining"] = round(dist / speed, 1)

                    if now - last_sec > 1.0:
                        self._emit_event("navigation.feedback", self.active_goal)

            # 4. Periodic telemetry broadcast (every 1 second)
            if now - last_sec >= 1.0:
                last_sec = now
                # Natural battery slow discharge
                if not self.is_charging:
                    self.battery_pct = max(15.0, round(self.battery_pct - 0.002, 3))
                else:
                    self.battery_pct = min(100.0, round(self.battery_pct + 0.02, 3))

                # Periodic telemetry event
                self._emit_event("robot.status", self.get_robot_status())

            time.sleep(0.05)

    def get_robot_status(self) -> Dict[str, Any]:
        return {
            "robot_id": self.robot_id,
            "name": self.name,
            "is_connected": True,
            "dev_mode": True,
            "operating_mode": self.operating_mode,
            "current_activity": self.current_activity,
            "expression": self.expression,
            "battery": {
                "percentage": round(self.battery_pct, 1),
                "voltage": self.battery_voltage,
                "current": 0.45,
                "is_charging": self.is_charging,
                "is_low": self.battery_pct < 20.0,
            },
            "location": {
                "x": round(self.pose_x, 3),
                "y": round(self.pose_y, 3),
                "theta": round(self.pose_theta, 3),
                "frame_id": "map",
            },
            "unacknowledged_emergencies": self.active_emergency_count,
            "next_medicine_reminder": "13:00 - Metformin",
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "system_status": "operational",
            "uptime_seconds": 4320.0,
            "cpu_usage_percent": 14.2,
            "memory_usage_percent": 38.6,
            "subsystems": {
                "ros2_bridge": "healthy (mock)",
                "camera_stream": "healthy",
                "navigation_stack": "healthy",
                "voice_assistant": "healthy",
                "vision_pipeline": "healthy",
                "esp32_serial": "healthy (loopback)",
                "database": "healthy",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def send_cmd_vel(self, linear_x: float, angular_z: float) -> bool:
        if self.operating_mode == "EMERGENCY_HALT":
            return False

        # Clamp to safety limits
        clamped_x = max(-settings.max_linear_speed, min(settings.max_linear_speed, linear_x))
        clamped_z = max(-settings.max_angular_speed, min(settings.max_angular_speed, angular_z))

        self.linear_x = clamped_x
        self.angular_z = clamped_z
        self.last_cmd_vel_time = time.time()
        self.current_activity = "manual_control" if (clamped_x != 0 or clamped_z != 0) else "idle"
        return True

    def stop_robot(self) -> bool:
        self.linear_x = 0.0
        self.angular_z = 0.0
        if self.active_goal:
            self.active_goal["status"] = "CANCELED"
            self._emit_event("navigation.canceled", self.active_goal)
        self.current_activity = "idle"
        return True

    def navigate_to_pose(self, x: float, y: float, theta: float, destination_name: str = "Target") -> Dict[str, Any]:
        dx = x - self.pose_x
        dy = y - self.pose_y
        dist = math.hypot(dx, dy)
        goal_id = f"nav-{uuid.uuid4().hex[:8]}"

        self.active_goal = {
            "goal_id": goal_id,
            "destination_name": destination_name,
            "target_x": round(x, 2),
            "target_y": round(y, 2),
            "status": "EXECUTING",
            "progress_percent": 0.0,
            "distance_remaining_m": round(dist, 2),
            "estimated_seconds_remaining": round(dist / 0.35, 1),
            "initial_distance": dist,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.current_activity = "navigating"
        self.expression = "thinking"
        self._emit_event("navigation.started", self.active_goal)
        return self.active_goal

    def cancel_navigation(self) -> bool:
        if self.active_goal and self.active_goal.get("status") == "EXECUTING":
            self.active_goal["status"] = "CANCELED"
            self.current_activity = "idle"
            self.expression = "happy"
            self._emit_event("navigation.canceled", self.active_goal)
            return True
        return False

    def get_navigation_status(self) -> Dict[str, Any]:
        if self.active_goal:
            return self.active_goal
        return {
            "goal_id": "none",
            "destination_name": "Idle",
            "target_x": self.pose_x,
            "target_y": self.pose_y,
            "status": "SUCCEEDED",
            "progress_percent": 100.0,
            "distance_remaining_m": 0.0,
            "estimated_seconds_remaining": 0.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def speak_phrase(self, phrase: str) -> bool:
        self.expression = "alert"
        self.voice_state = "speaking"
        self._emit_event("voice.speaking", {"phrase": phrase})
        return True

    def send_voice_command(self, command: str) -> Dict[str, Any]:
        cmd_lower = command.lower()
        if "stop" in cmd_lower or "halt" in cmd_lower:
            self.stop_robot()
            resp = "Stopping all movement immediately."
        elif "where are you" in cmd_lower or "location" in cmd_lower:
            resp = f"I am currently located at coordinates ({self.pose_x:.1f}, {self.pose_y:.1f}) in the living space."
        elif "medicine" in cmd_lower or "reminder" in cmd_lower:
            resp = "Your next scheduled medicine is Metformin (500mg) at 1:00 PM."
        elif "battery" in cmd_lower:
            resp = f"My battery is currently at {self.battery_pct:.0f}% charge and operational."
        elif "help" in cmd_lower:
            resp = "I am LUMI, your companion. You can ask me to navigate, check medicine, or assist you."
        else:
            resp = f"I received your request: '{command}'. I am monitoring your health and surroundings."

        self.last_transcript = command
        self.last_response = resp
        self._emit_event("voice.response", {"command": command, "response": resp})
        return {
            "id": f"vox-{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recognized_speech": command,
            "response_text": resp,
            "speaker": "LUMI",
            "source": "mock_llm",
        }

    def trigger_medicine_reminder(self, medicine_name: str, dosage: str) -> bool:
        self.current_activity = "reminder"
        self.expression = "alert"
        phrase = f"Hello! It is time to take your scheduled medicine: {medicine_name}, {dosage}."
        self.speak_phrase(phrase)
        self._emit_event("medicine.reminder", {
            "medicine_name": medicine_name,
            "dosage": dosage,
            "phrase": phrase,
        })
        return True

    def acknowledge_medicine_reminder(self) -> bool:
        if self.current_activity == "reminder":
            self.current_activity = "idle"
            self.expression = "happy"
        self._emit_event("medicine.acknowledgement", {
            "status": "acknowledged",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return True

    def get_person_tracks(self) -> List[Dict[str, Any]]:
        return [
            {
                "track_id": 1,
                "person_name": self.person_name,
                "confidence": 0.94,
                "posture": self.current_posture,
                "presence_state": self.presence_state,
                "last_seen_timestamp": datetime.now(timezone.utc).isoformat(),
                "bbox": [180, 80, 460, 420],
            }
        ]

    def get_audio_devices(self) -> List[Dict[str, Any]]:
        return [
            {"id": 0, "name": "USB Audio Device (LUMI Mic)", "device_type": "input", "is_default": True},
            {"id": 1, "name": "USB Audio Device (LUMI Speaker)", "device_type": "output", "is_default": True},
            {"id": 2, "name": "Built-in Raspberry Pi HDMI Audio", "device_type": "output", "is_default": False},
        ]

    def test_audio_device(self, phrase: str, device_id: Optional[int] = None) -> bool:
        self.speak_phrase(phrase)
        return True

    def get_latest_camera_frame(self) -> Optional[bytes]:
        """
        Generates realistic 640x480 RGB camera frame with LUMI status overlay,
        mock person silhouette/bounding box, and live timestamp.
        """
        width, height = 640, 480
        # Create subtle gradient background simulating indoor room
        img = Image.new("RGB", (width, height), color=(35, 30, 45))
        draw = ImageDraw.Draw(img)

        # Draw indoor room elements (floor and walls)
        draw.rectangle([0, 360, width, height], fill=(50, 45, 60))
        draw.line([0, 360, width, 360], fill=(70, 65, 80), width=2)

        # Draw simulated human figure in room
        person_box = [240, 100, 400, 400]
        # Bounding box
        draw.rectangle(person_box, outline=(0, 230, 120), width=2)
        # Person head and torso
        draw.ellipse([290, 110, 350, 170], fill=(90, 80, 110), outline=(0, 230, 120))
        draw.rectangle([280, 175, 360, 330], fill=(80, 70, 100))
        draw.rectangle([285, 330, 315, 395], fill=(60, 50, 80))
        draw.rectangle([325, 330, 355, 395], fill=(60, 50, 80))

        # Person label badge
        badge_text = f"Primary Patient | Posture: {self.current_posture.upper()}"
        draw.rectangle([235, 75, 415, 98], fill=(0, 200, 100))
        draw.text((240, 80), badge_text, fill=(0, 0, 0))

        # Top overlay bar: LUMI Camera Status
        draw.rectangle([0, 0, width, 40], fill=(20, 15, 30, 200))
        ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((15, 12), f"LUMI LIVE CAMERA [MOCK DEV MODE] - {ts_str}", fill=(240, 230, 255))
        draw.text((530, 12), "30 FPS | HD", fill=(0, 230, 120))

        # Bottom info bar
        draw.rectangle([0, 440, width, height], fill=(20, 15, 30, 200))
        info_text = f"Robot Pose: ({self.pose_x:.1f}, {self.pose_y:.1f}) | Batt: {self.battery_pct:.0f}% | Mode: {self.operating_mode}"
        draw.text((15, 452), info_text, fill=(200, 190, 220))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
