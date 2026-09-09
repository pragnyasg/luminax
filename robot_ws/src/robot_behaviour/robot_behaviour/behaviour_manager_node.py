#!/usr/bin/env python3
"""
Finite State Machine (FSM) Behaviour Manager Node for Baymax Healthcare Robot.

States:
- IDLE: Resting at base station, monitoring sensors.
- NAVIGATING: Executing Nav2 navigation goal path.
- INTERACTING: Person detected; rendering greetings & companion feedback.
- REMINDER: Processing active medicine reminder schedule.
- EMERGENCY: Escalating unacknowledged emergency check ("Are you okay?").
"""

from enum import Enum
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class RobotState(Enum):
    IDLE = "IDLE"
    NAVIGATING = "NAVIGATING"
    INTERACTING = "INTERACTING"
    REMINDER = "REMINDER"
    EMERGENCY = "EMERGENCY"


class BehaviourManagerNode(Node):
    def __init__(self):
        super().__init__('behaviour_manager_node')

        # Current State
        self.state = RobotState.IDLE

        # ROS 2 Subscribers
        self.sub_person = self.create_subscription(
            Bool,
            '/perception/person_detected',
            self.person_detected_callback,
            10
        )

        self.sub_reminder = self.create_subscription(
            String,
            '/health/reminder_trigger',
            self.reminder_callback,
            10
        )

        self.sub_voice_cmd = self.create_subscription(
            String,
            '/voice/command',
            self.voice_cmd_callback,
            10
        )

        # ROS 2 Publishers
        self.pub_state = self.create_publisher(String, '/behaviour/current_state', 10)
        self.pub_speak = self.create_publisher(String, '/voice/speak', 10)

        # 10Hz FSM State Publishing Timer
        self.timer = self.create_timer(0.1, self.fsm_loop)

        self.get_logger().info('Behaviour Manager FSM Node initialized in IDLE state.')

    def set_state(self, new_state: RobotState, reason: str = ""):
        """Transitions FSM to a new state with logging."""
        if self.state != new_state:
            self.get_logger().info(f'[FSM TRANSITION]: {self.state.value} -> {new_state.value} (Reason: {reason})')
            self.state = new_state

    def person_detected_callback(self, msg: Bool):
        """Triggered when perception detects human in view."""
        person_present = msg.data
        if person_present and self.state == RobotState.IDLE:
            self.set_state(RobotState.INTERACTING, "Person detected in camera field of view")
            speak_msg = String()
            speak_msg.data = "Hello! I am Baymax, your personal healthcare companion."
            self.pub_speak.publish(speak_msg)
        elif not person_present and self.state == RobotState.INTERACTING:
            self.set_state(RobotState.IDLE, "Person left camera field of view")

    def reminder_callback(self, msg: String):
        """Triggered when healthcare reminder manager fires an alarm."""
        if self.state != RobotState.EMERGENCY:
            self.set_state(RobotState.REMINDER, f"Medicine alarm: {msg.data}")

    def voice_cmd_callback(self, msg: String):
        """Handles voice command state resets."""
        cmd = msg.data.lower()
        if "stop" in cmd:
            self.set_state(RobotState.IDLE, "Voice emergency stop command received")
            speak_msg = String()
            speak_msg.data = "Stopping all navigation and returning to idle state."
            self.pub_speak.publish(speak_msg)

    def fsm_loop(self):
        """10Hz Loop publishing current state for system status monitoring."""
        state_msg = String()
        state_msg.data = self.state.value
        self.pub_state.publish(state_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BehaviourManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
