#!/usr/bin/env python3
"""
Healthcare Reminder Manager ROS 2 Node for LUMI Healthcare Robot.

This node performs:
1. Manages scheduled medicine reminders via periodic ROS 2 timers.
2. Triggers voice prompts on /voice/speak ("Time to take your scheduled medicine.").
3. Monitors patient acknowledgment via voice command (/voice/command) or service call.
4. Escalates unacknowledged reminders to emergency alerts on /health/emergency_alert.
5. Provides ROS 2 Trigger services:
   - /health/trigger_reminder (trigger immediate reminder)
   - /health/acknowledge_reminder (acknowledge pending reminder)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from std_srvs.srv import Trigger


class ReminderManagerNode(Node):
    def __init__(self):
        super().__init__('reminder_manager_node')

        # Declare Parameters
        self.declare_parameter('reminder_interval', 60.0)    # Interval between periodic reminders (seconds)
        self.declare_parameter('escalation_timeout', 30.0)   # Seconds unacknowledged before triggering emergency
        self.declare_parameter('auto_schedule', True)        # Automatically trigger periodic reminders

        self.reminder_interval = self.get_parameter('reminder_interval').value
        self.escalation_timeout = self.get_parameter('escalation_timeout').value
        self.auto_schedule = self.get_parameter('auto_schedule').value

        # Publishers
        self.pub_reminder = self.create_publisher(String, '/health/reminder_trigger', 10)
        self.pub_speak = self.create_publisher(String, '/voice/speak', 10)
        self.pub_emergency = self.create_publisher(String, '/health/emergency_alert', 10)
        self.pub_status = self.create_publisher(Bool, '/health/reminder_pending', 10)

        # Subscribers
        self.sub_voice_cmd = self.create_subscription(
            String,
            '/voice/command',
            self.voice_cmd_callback,
            10
        )

        # Services
        self.srv_trigger = self.create_service(
            Trigger,
            '/health/trigger_reminder',
            self.srv_trigger_callback
        )

        self.srv_ack = self.create_service(
            Trigger,
            '/health/acknowledge_reminder',
            self.srv_ack_callback
        )

        # State Variables
        self.is_reminder_active = False
        self.reminder_count = 0
        self.reminder_start_time = None

        # Timers
        if self.auto_schedule and self.reminder_interval > 0:
            self.timer_reminder = self.create_timer(self.reminder_interval, self.trigger_reminder)

        # 1 Hz escalation check timer
        self.timer_escalation = self.create_timer(1.0, self.check_escalation)

        self.get_logger().info(
            f'Reminder Manager Node active. Interval: {self.reminder_interval}s, Escalation: {self.escalation_timeout}s.'
        )

    def trigger_reminder(self):
        """Fires scheduled medicine reminder alert."""
        self.reminder_count += 1
        self.is_reminder_active = True
        self.reminder_start_time = self.get_clock().now()

        msg_text = f"Reminder #{self.reminder_count}: Scheduled medicine due."
        self.get_logger().info(f'[HEALTH REMINDER]: {msg_text}')

        rem_msg = String()
        rem_msg.data = msg_text
        self.pub_reminder.publish(rem_msg)

        speak_msg = String()
        speak_msg.data = "Hello! I am LUMI. It is time for your scheduled medicine."
        self.pub_speak.publish(speak_msg)

        self._publish_pending_status(True)

    def check_escalation(self):
        """Checks if active reminder has exceeded escalation timeout without acknowledgment."""
        if not self.is_reminder_active or self.reminder_start_time is None:
            return

        elapsed = (self.get_clock().now() - self.reminder_start_time).nanoseconds / 1e9
        if elapsed >= self.escalation_timeout:
            # Escalate to emergency
            alert_text = f"ALERT: Medicine reminder #{self.reminder_count} unacknowledged after {int(elapsed)}s!"
            self.get_logger().warn(f'[ESCALATION]: {alert_text}')

            alert_msg = String()
            alert_msg.data = alert_text
            self.pub_emergency.publish(alert_msg)

            speak_msg = String()
            speak_msg.data = "Warning! Medicine reminder unacknowledged. Contacting caregiver."
            self.pub_speak.publish(speak_msg)

            # Reset timer so we don't spam every second
            self.reminder_start_time = self.get_clock().now()

    def acknowledge_reminder(self, source: str = "user"):
        """Acknowledges current reminder and returns acknowledgment confirmation."""
        if self.is_reminder_active:
            self.is_reminder_active = False
            self.reminder_start_time = None
            self.get_logger().info(f'[REMINDER ACKNOWLEDGED via {source}] Patient confirmed medicine taken.')

            speak_msg = String()
            speak_msg.data = "Thank you. I have confirmed your medicine was taken."
            self.pub_speak.publish(speak_msg)

            self._publish_pending_status(False)
            return True
        return False

    def voice_cmd_callback(self, msg: String):
        """Parses voice keywords for medicine acknowledgment."""
        cmd = msg.data.lower()
        if any(keyword in cmd for keyword in ["medicine", "taken", "yes", "confirm", "okay", "done"]):
            self.acknowledge_reminder(source="voice")

    def srv_trigger_callback(self, request, response):
        """Service callback to trigger reminder on demand."""
        self.trigger_reminder()
        response.success = True
        response.message = f"Triggered reminder #{self.reminder_count}"
        return response

    def srv_ack_callback(self, request, response):
        """Service callback to acknowledge reminder programmatically."""
        was_active = self.acknowledge_reminder(source="service")
        response.success = was_active
        response.message = "Reminder acknowledged successfully" if was_active else "No active reminder to acknowledge"
        return response

    def _publish_pending_status(self, pending: bool):
        status_msg = Bool()
        status_msg.data = pending
        self.pub_status.publish(status_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ReminderManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
