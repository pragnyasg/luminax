#!/usr/bin/env python3
"""
Finite State Machine (FSM) Behaviour Manager Node for LUMI Healthcare Robot.

States:
- IDLE: Resting, monitoring sensors and listening for alerts.
- NAVIGATING: Executing autonomous goal navigation.
- INTERACTING: Person detected in view; greeting and interacting.
- REMINDER: Active medicine reminder in progress.
- EMERGENCY: Escalated alarm or unacknowledged emergency; robot safely halts.
"""

from enum import Enum
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger


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

        # Subscribers
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

        self.sub_emergency = self.create_subscription(
            String,
            '/health/emergency_alert',
            self.emergency_callback,
            10
        )

        self.sub_voice_cmd = self.create_subscription(
            String,
            '/voice/command',
            self.voice_cmd_callback,
            10
        )

        # Publishers
        self.pub_state = self.create_publisher(String, '/behaviour/current_state', 10)
        self.pub_speak = self.create_publisher(String, '/voice/speak', 10)
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        # Service to manually reset state
        self.srv_reset = self.create_service(
            Trigger,
            '/behaviour/reset_state',
            self.srv_reset_callback
        )

        # 10 Hz FSM Loop Timer
        self.timer = self.create_timer(0.1, self.fsm_loop)

        self.get_logger().info('LUMI Behaviour Manager FSM initialized in IDLE state.')

    def set_state(self, new_state: RobotState, reason: str = ""):
        """Transitions FSM to a new state with structured logging."""
        if self.state != new_state:
            self.get_logger().info(
                f'[FSM TRANSITION]: {self.state.value} -> {new_state.value} (Reason: {reason})'
            )
            self.state = new_state

            # If transitioning to emergency, command immediate zero velocity
            if new_state == RobotState.EMERGENCY:
                self._stop_robot()

    def _stop_robot(self):
        """Publishes explicit zero twist to ensure physical and simulated safety."""
        stop_twist = Twist()
        self.pub_cmd_vel.publish(stop_twist)

    def person_detected_callback(self, msg: Bool):
        """Triggered when human detection perception status changes."""
        person_present = msg.data
        if person_present and self.state == RobotState.IDLE:
            self.set_state(RobotState.INTERACTING, "Human detected in camera view")
            speak_msg = String()
            speak_msg.data = "Hello! I am LUMI, your personal healthcare companion."
            self.pub_speak.publish(speak_msg)
        elif not person_present and self.state == RobotState.INTERACTING:
            self.set_state(RobotState.IDLE, "Human left camera view")

    def reminder_callback(self, msg: String):
        """Triggered when healthcare reminder manager fires an alarm."""
        if self.state != RobotState.EMERGENCY:
            self.set_state(RobotState.REMINDER, f"Medicine alarm: {msg.data}")

    def emergency_callback(self, msg: String):
        """Triggered when healthcare reminder escalates or emergency occurs."""
        self.set_state(RobotState.EMERGENCY, f"Emergency alert: {msg.data}")

    def voice_cmd_callback(self, msg: String):
        """Handles voice commands for emergency stop or state reset."""
        cmd = msg.data.lower()
        if "stop" in cmd or "halt" in cmd:
            self.set_state(RobotState.IDLE, "Voice stop command received")
            self._stop_robot()
            speak_msg = String()
            speak_msg.data = "Stopping all movement."
            self.pub_speak.publish(speak_msg)
        elif "reset" in cmd or "clear" in cmd or "resume" in cmd:
            self.set_state(RobotState.IDLE, "Voice reset command received")
            speak_msg = String()
            speak_msg.data = "Emergency cleared. Resuming normal operations."
            self.pub_speak.publish(speak_msg)

    def srv_reset_callback(self, request, response):
        """Service callback to reset state to IDLE."""
        prev = self.state.value
        self.set_state(RobotState.IDLE, "Service reset request")
        response.success = True
        response.message = f"FSM transitioned from {prev} to IDLE"
        return response

    def fsm_loop(self):
        """10 Hz Loop publishing current status."""
        state_msg = String()
        state_msg.data = self.state.value
        self.pub_state.publish(state_msg)

        if self.state == RobotState.EMERGENCY:
            # Continually reinforce safe stop in emergency
            self._stop_robot()


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
