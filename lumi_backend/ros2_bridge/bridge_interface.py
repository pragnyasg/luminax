"""
Abstract Base Interface for Robot Communication.
Provides a strictly typed, unified contract for both the real ROS 2 Bridge and the Mock Bridge.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, List, Optional


class RobotBridgeBase(ABC):
    @abstractmethod
    def start(self) -> None:
        """Start background threads, subscriptions, or mock timers."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Gracefully terminate background runners."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """True if bridge has live active communication with robot hardware / simulator."""
        pass

    @abstractmethod
    def get_robot_status(self) -> Dict[str, Any]:
        """Returns structured robot status dictionary matching RobotStatus schema."""
        pass

    @abstractmethod
    def get_diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostics for all subsystems."""
        pass

    @abstractmethod
    def send_cmd_vel(self, linear_x: float, angular_z: float) -> bool:
        """Transmits velocity commands with safety speed limits and dead-man protection."""
        pass

    @abstractmethod
    def stop_robot(self) -> bool:
        """Commands immediate zero-velocity halt."""
        pass

    @abstractmethod
    def navigate_to_pose(self, x: float, y: float, theta: float, destination_name: str = "Target") -> Dict[str, Any]:
        """Dispatches an autonomous navigation goal to Nav2 or simulated controller."""
        pass

    @abstractmethod
    def cancel_navigation(self) -> bool:
        """Aborts the currently active navigation goal."""
        pass

    @abstractmethod
    def get_navigation_status(self) -> Dict[str, Any]:
        """Returns active navigation goal progress, state, and distance remaining."""
        pass

    @abstractmethod
    def speak_phrase(self, phrase: str) -> bool:
        """Commands the robot text-to-speech engine to speak immediately."""
        pass

    @abstractmethod
    def send_voice_command(self, command: str) -> Dict[str, Any]:
        """Injects a text command into the robot voice/behaviour pipeline."""
        pass

    @abstractmethod
    def trigger_medicine_reminder(self, medicine_name: str, dosage: str) -> bool:
        """Triggers the robot reminder manager node with spoken alert."""
        pass

    @abstractmethod
    def acknowledge_medicine_reminder(self) -> bool:
        """Acknowledges currently active medicine alert on the robot."""
        pass

    @abstractmethod
    def get_person_tracks(self) -> List[Dict[str, Any]]:
        """Returns list of tracked and recognized individuals in camera view."""
        pass

    @abstractmethod
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """Returns list of hardware audio input/output devices on the robot."""
        pass

    @abstractmethod
    def test_audio_device(self, phrase: str, device_id: Optional[int] = None) -> bool:
        """Plays test audio through robot speaker."""
        pass

    @abstractmethod
    def get_latest_camera_frame(self) -> Optional[bytes]:
        """Returns raw JPEG bytes of latest camera frame."""
        pass

    @abstractmethod
    def register_event_callback(self, callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]) -> None:
        """Registers async callback invoked when robot-originated events occur."""
        pass
