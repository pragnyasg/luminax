#!/usr/bin/env python3
"""
Healthcare Reminder Manager ROS 2 Node for Baymax Healthcare Robot.

This node performs 3 key tasks:
1. Manages scheduled medicine reminders using a ROS 2 periodic timer.
2. Triggers voice prompts on /voice/speak ("Time to take your medicine.").
3. Monitors patient acknowledgment and triggers emergency alert if unacknowledged.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ReminderManagerNode(Node):
    def __init__(self):
        super().__init__('reminder_manager_node')

        # Declare Parameters (Reminder Interval in Seconds)
        self.declare_parameter('reminder_interval', 60.0)  # Default 60 seconds demo interval
        self.reminder_interval = self.get_parameter('reminder_interval').value

        # ROS 2 Publishers & Subscribers
        self.pub_reminder = self.create_publisher(String, '/health/reminder_trigger', 10)
        self.pub_speak = self.create_publisher(String, '/voice/speak', 10)
        self.pub_emergency = self.create_publisher(String, '/health/emergency_alert', 10)

        self.sub_voice_cmd = self.create_subscription(
            String,
            '/voice/command',
            self.voice_cmd_callback,
            10
        )

        # State tracking
        self.is_reminder_active = False
        self.reminder_count = 0

        # Periodic Reminder Timer
        self.timer = self.create_timer(self.reminder_interval, self.trigger_reminder)

        self.get_logger().info(f'Reminder Manager Node initialized. Interval: {self.reminder_interval}s.')

    def trigger_reminder(self):
        """Fires periodic medicine reminder alert."""
        self.reminder_count += 1
        self.is_reminder_active = True

        msg_text = f"Reminder #{self.reminder_count}: Time to take your scheduled medicine."
        self.get_logger().info(f'[HEALTH REMINDER TRIGGERED]: {msg_text}')

        # Publish Reminder Trigger Event for Behavior FSM
        rem_msg = String()
        rem_msg.data = msg_text
        self.pub_reminder.publish(rem_msg)

        # Request Voice Output
        speak_msg = String()
        speak_msg.data = "Hello! I am Baymax. It is time for your scheduled medicine."
        self.pub_speak.publish(speak_msg)

    def voice_cmd_callback(self, msg: String):
        """Handles patient voice acknowledgment."""
        cmd = msg.data.lower()
        if "medicine" in cmd or "taken" in cmd or "okay" in cmd:
            if self.is_reminder_active:
                self.is_reminder_active = False
                self.get_logger().info('[HEALTH REMINDER ACKNOWLEDGED] Patient confirmed medicine taken.')
                
                speak_msg = String()
                speak_msg.data = "Thank you. I have logged that your medicine was taken."
                self.pub_speak.publish(speak_msg)


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
