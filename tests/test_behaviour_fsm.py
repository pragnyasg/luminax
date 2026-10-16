#!/usr/bin/env python3
"""
Unit Tests for LUMI Behaviour Manager Finite State Machine (FSM).
"""

from enum import Enum
import unittest


class RobotState(Enum):
    IDLE = "IDLE"
    NAVIGATING = "NAVIGATING"
    INTERACTING = "INTERACTING"
    REMINDER = "REMINDER"
    EMERGENCY = "EMERGENCY"


class MockFSM:
    """Pure Python FSM logic extracted for deterministic platform-independent unit testing."""
    def __init__(self):
        self.state = RobotState.IDLE
        self.last_speech = None
        self.emergency_stopped = False

    def on_person_detected(self, detected: bool):
        if detected and self.state == RobotState.IDLE:
            self.state = RobotState.INTERACTING
            self.last_speech = "Hello! I am LUMI, your personal healthcare companion."
        elif not detected and self.state == RobotState.INTERACTING:
            self.state = RobotState.IDLE

    def on_reminder_trigger(self, msg: str):
        if self.state != RobotState.EMERGENCY:
            self.state = RobotState.REMINDER

    def on_emergency_alert(self, msg: str):
        self.state = RobotState.EMERGENCY
        self.emergency_stopped = True

    def on_voice_command(self, cmd: str):
        cmd = cmd.lower()
        if "stop" in cmd or "halt" in cmd:
            self.state = RobotState.IDLE
            self.emergency_stopped = True
            self.last_speech = "Stopping all movement."
        elif "reset" in cmd or "clear" in cmd or "resume" in cmd:
            self.state = RobotState.IDLE
            self.emergency_stopped = False
            self.last_speech = "Emergency cleared. Resuming normal operations."


class TestBehaviourFSM(unittest.TestCase):
    def setUp(self):
        self.fsm = MockFSM()

    def test_initial_state(self):
        self.assertEqual(self.fsm.state, RobotState.IDLE)
        self.assertFalse(self.fsm.emergency_stopped)

    def test_person_detection_interaction(self):
        self.fsm.on_person_detected(True)
        self.assertEqual(self.fsm.state, RobotState.INTERACTING)
        self.assertIn("LUMI", self.fsm.last_speech)

        # Person leaves
        self.fsm.on_person_detected(False)
        self.assertEqual(self.fsm.state, RobotState.IDLE)

    def test_reminder_transition(self):
        self.fsm.on_reminder_trigger("Pill time")
        self.assertEqual(self.fsm.state, RobotState.REMINDER)

    def test_emergency_escalation(self):
        self.fsm.on_emergency_alert("Patient fell or reminder unacknowledged")
        self.assertEqual(self.fsm.state, RobotState.EMERGENCY)
        self.assertTrue(self.fsm.emergency_stopped)

        # In emergency, normal reminders should not overwrite emergency state
        self.fsm.on_reminder_trigger("Next pill")
        self.assertEqual(self.fsm.state, RobotState.EMERGENCY)

    def test_voice_stop_and_reset(self):
        self.fsm.on_person_detected(True)
        self.assertEqual(self.fsm.state, RobotState.INTERACTING)

        self.fsm.on_voice_command("Emergency stop immediately!")
        self.assertEqual(self.fsm.state, RobotState.IDLE)
        self.assertTrue(self.fsm.emergency_stopped)

        self.fsm.on_voice_command("Clear and resume")
        self.assertEqual(self.fsm.state, RobotState.IDLE)
        self.assertFalse(self.fsm.emergency_stopped)


if __name__ == '__main__':
    unittest.main()
