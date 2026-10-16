#!/usr/bin/env python3
"""
Serial Bridge & Wheel Odometry ROS 2 Node for LUMI Healthcare Robot.

This node performs 5 key tasks:
1. Subscribes to /cmd_vel (geometry_msgs/msg/Twist) from Nav2 or teleop.
2. Applies differential-drive kinematics to compute left/right wheel speeds (v_L, v_R).
3. Transmits target velocities over USB Serial to ESP32 (or software loopback when offline).
4. Decodes encoder tick telemetry and battery voltage from ESP32.
5. Computes odometry (pose & twist) and broadcasts /odom and TF (odom -> base_footprint).
"""

import json
import math
import sys
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import BatteryState
import tf2_ros

try:
    import serial
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False


class SerialBridgeNode(Node):
    def __init__(self):
        super().__init__('serial_bridge_node')

        # Declare ROS 2 Parameters
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('wheel_track', 0.32)      # 32 cm separation between wheel centers
        self.declare_parameter('wheel_radius', 0.04)     # 4 cm radius (8 cm diameter wheel)
        self.declare_parameter('encoder_cpr', 334.0)     # Counts per revolution
        self.declare_parameter('publish_tf', True)       # Broadcast odom -> base_footprint TF
        self.declare_parameter('cmd_vel_timeout', 0.5)   # Seconds before stopping if no cmd_vel

        # Retrieve Parameter Values
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.wheel_track = self.get_parameter('wheel_track').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.encoder_cpr = self.get_parameter('encoder_cpr').value
        self.publish_tf = self.get_parameter('publish_tf').value
        self.cmd_vel_timeout = self.get_parameter('cmd_vel_timeout').value

        # Robot Pose & Velocity State Variables
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v_left_target = 0.0
        self.v_right_target = 0.0
        self.last_cmd_vel_time = self.get_clock().now()
        self.last_time = self.get_clock().now()

        # Encoder tracking for tick-to-displacement conversion
        self.prev_enc_l = None
        self.prev_enc_r = None

        # Hardware Serial Connection Setup
        self.serial_port = None
        self.is_hardware_connected = False
        self._init_serial()

        # ROS 2 Subscribers and Publishers
        self.sub_cmd_vel = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.pub_odom = self.create_publisher(Odometry, '/odom', 10)
        self.pub_battery = self.create_publisher(BatteryState, '/battery_state', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # 20 Hz Update Loop Timer (50 ms)
        self.timer = self.create_timer(0.05, self.update_loop)

        self.get_logger().info('LUMI Serial Bridge & Odometry Node initialized.')

    def _init_serial(self):
        """Attempt to open hardware serial port to ESP32."""
        if not HAS_SERIAL:
            self.get_logger().warn('pyserial not installed. Operating in software loopback mode.')
            return

        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.05)
            self.is_hardware_connected = True
            self.get_logger().info(f'Connected to ESP32 on {self.port} at {self.baudrate} baud.')
        except Exception as e:
            self.is_hardware_connected = False
            self.get_logger().warn(
                f'Could not open serial port {self.port}: {e}. Operating in software loopback simulation mode.'
            )

    def cmd_vel_callback(self, msg: Twist):
        """
        Translates Twist velocity command to differential left/right wheel speeds.
        Kinematics:
          v_left  = v - (omega * wheel_track / 2)
          v_right = v + (omega * wheel_track / 2)
        """
        self.last_cmd_vel_time = self.get_clock().now()
        linear_v = msg.linear.x
        angular_w = msg.angular.z

        self.v_left_target = linear_v - (angular_w * self.wheel_track / 2.0)
        self.v_right_target = linear_v + (angular_w * self.wheel_track / 2.0)

        self._send_speed_command(self.v_left_target, self.v_right_target)

    def _send_speed_command(self, v_l: float, v_r: float):
        """Transmits target wheel velocities as JSON string to ESP32."""
        if self.is_hardware_connected and self.serial_port:
            packet = {
                "cmd": "vel",
                "v_l": round(v_l, 3),
                "v_r": round(v_r, 3)
            }
            try:
                line = json.dumps(packet) + "\n"
                self.serial_port.write(line.encode('utf-8'))
            except Exception as e:
                self.get_logger().error(f'Error writing to ESP32 serial: {e}')

    def update_loop(self):
        """
        20 Hz Loop:
        1. Checks watchdog timeout on /cmd_vel.
        2. Reads encoder telemetry & battery voltage from ESP32.
        3. Integrates differential-drive forward kinematics.
        4. Publishes /odom and /battery_state, and optionally broadcasts TF.
        """
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        if dt <= 0.0:
            return

        # Watchdog: Stop motors if command velocity stream times out
        time_since_cmd = (current_time - self.last_cmd_vel_time).nanoseconds / 1e9
        if time_since_cmd > self.cmd_vel_timeout:
            if self.v_left_target != 0.0 or self.v_right_target != 0.0:
                self.v_left_target = 0.0
                self.v_right_target = 0.0
                self._send_speed_command(0.0, 0.0)

        d_left = 0.0
        d_right = 0.0
        have_telemetry = False

        # Read serial telemetry from ESP32 if available
        if self.is_hardware_connected and self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    data = json.loads(line)
                    # Case 1: ESP32 sends encoder tick counts
                    if 'enc_l' in data and 'enc_r' in data:
                        enc_l = int(data['enc_l'])
                        enc_r = int(data['enc_r'])

                        if self.prev_enc_l is not None and self.prev_enc_r is not None:
                            delta_l = enc_l - self.prev_enc_l
                            delta_r = enc_r - self.prev_enc_r
                            # Convert ticks to distance in meters
                            meters_per_tick = (2.0 * math.pi * self.wheel_radius) / self.encoder_cpr
                            d_left = delta_l * meters_per_tick
                            d_right = delta_r * meters_per_tick
                            have_telemetry = True

                        self.prev_enc_l = enc_l
                        self.prev_enc_r = enc_r

                    # Case 2: ESP32 sends precomputed delta displacements
                    elif 'd_l' in data and 'd_r' in data:
                        d_left = float(data['d_l'])
                        d_right = float(data['d_r'])
                        have_telemetry = True

                    # Battery voltage telemetry
                    if 'v_bat' in data:
                        v_bat = float(data['v_bat'])
                        bat_msg = BatteryState()
                        bat_msg.header.stamp = current_time.to_msg()
                        bat_msg.header.frame_id = 'base_link'
                        bat_msg.voltage = v_bat
                        # 12V Li-ion battery estimation (nominal 12.0V, max 12.6V, min 10.5V)
                        percentage = max(0.0, min(1.0, (v_bat - 10.5) / (12.6 - 10.5)))
                        bat_msg.percentage = percentage
                        self.pub_battery.publish(bat_msg)

            except Exception as e:
                pass

        # Fallback to software loopback kinematics simulation when offline
        if not have_telemetry:
            d_left = self.v_left_target * dt
            d_right = self.v_right_target * dt

        # Differential Drive Forward Kinematics Integration (Runge-Kutta / midpoint)
        d_center = (d_right + d_left) / 2.0
        d_theta = (d_right - d_left) / self.wheel_track

        self.x += d_center * math.cos(self.theta + d_theta / 2.0)
        self.y += d_center * math.sin(self.theta + d_theta / 2.0)
        self.theta += d_theta

        # Normalize heading to [-pi, pi]
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        v_linear = d_center / dt
        v_angular = d_theta / dt

        # Convert 2D planar heading to quaternion representation
        qz = math.sin(self.theta / 2.0)
        qw = math.cos(self.theta / 2.0)

        # 1. Publish TF: odom -> base_footprint (if enabled)
        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = current_time.to_msg()
            t.header.frame_id = 'odom'
            t.child_frame_id = 'base_footprint'
            t.transform.translation.x = self.x
            t.transform.translation.y = self.y
            t.transform.translation.z = 0.0
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = qz
            t.transform.rotation.w = qw
            self.tf_broadcaster.sendTransform(t)

        # 2. Publish Odometry message on /odom
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation.x = 0.0
        odom_msg.pose.pose.orientation.y = 0.0
        odom_msg.pose.pose.orientation.z = qz
        odom_msg.pose.pose.orientation.w = qw

        odom_msg.twist.twist.linear.x = v_linear
        odom_msg.twist.twist.linear.y = 0.0
        odom_msg.twist.twist.angular.z = v_angular

        # Covariance matrices (diagonal estimates)
        odom_msg.pose.covariance[0] = 0.01   # x
        odom_msg.pose.covariance[7] = 0.01   # y
        odom_msg.pose.covariance[35] = 0.03  # yaw
        odom_msg.twist.covariance[0] = 0.01
        odom_msg.twist.covariance[35] = 0.03

        self.pub_odom.publish(odom_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
