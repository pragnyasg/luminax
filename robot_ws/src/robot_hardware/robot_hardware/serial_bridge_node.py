#!/usr/bin/env python3
"""
Serial Bridge & Wheel Odometry ROS 2 Node for Baymax Healthcare Robot.

This node performs 3 key tasks:
1. Subscribes to /cmd_vel (Twist messages) from Nav2 or teleop.
2. Translates linear velocity (v) and angular velocity (w) into left/right wheel speeds (v_L, v_R).
3. Transmits target velocities over USB Serial to the ESP32 microcontroller (or runs in loopback mode if offline).
4. Computes robot odometry (x, y, theta) from encoder tick telemetry and publishes /odom and TF odom -> base_footprint.
"""

import json
import math
import sys
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
import tf2_ros

# Try importing pyserial for hardware communication
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
        self.declare_parameter('wheel_track', 0.32)   # Distance between wheels (m)
        self.declare_parameter('wheel_radius', 0.04)  # Wheel radius (m)
        self.declare_parameter('encoder_cpr', 334.0)  # Encoder counts per revolution

        # Retrieve Parameter Values
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.wheel_track = self.get_parameter('wheel_track').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.encoder_cpr = self.get_parameter('encoder_cpr').value

        # Robot State Variables for Odometry
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v_left_target = 0.0
        self.v_right_target = 0.0
        self.last_time = self.get_clock().now()

        # Hardware Serial Connection Setup
        self.serial_port = None
        self.is_hardware_connected = False
        self._init_serial()

        # ROS 2 Subscribers, Publishers & TF Broadcasters
        self.sub_cmd_vel = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.pub_odom = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # 20 Hz Update Loop Timer
        self.timer = self.create_timer(0.05, self.update_loop)

        self.get_logger().info('Serial Bridge & Odometry Node initialized successfully.')

    def _init_serial(self):
        """Attempt to connect to physical ESP32 USB serial port."""
        if not HAS_SERIAL:
            self.get_logger().warn('PySerial module not installed. Running in software loopback mode.')
            return

        try:
            self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.is_hardware_connected = True
            self.get_logger().info(f'Connected to hardware ESP32 serial port on {self.port} at {self.baudrate} baud.')
        except Exception as e:
            self.is_hardware_connected = False
            self.get_logger().warn(f'Could not open serial port {self.port}: {e}. Operating in software loopback simulation mode.')

    def cmd_vel_callback(self, msg: Twist):
        """
        Translates ROS 2 Twist velocity commands into differential wheel speeds.
        
        Kinematic Equations:
        v_left  = linear.x - (angular.z * wheel_track / 2)
        v_right = linear.x + (angular.z * wheel_track / 2)
        """
        linear_v = msg.linear.x
        angular_w = msg.angular.z

        self.v_left_target = linear_v - (angular_w * self.wheel_track / 2.0)
        self.v_right_target = linear_v + (angular_w * self.wheel_track / 2.0)

        # Send command to hardware ESP32 if connected
        if self.is_hardware_connected and self.serial_port:
            packet = {
                "cmd": "vel",
                "v_l": round(self.v_left_target, 3),
                "v_r": round(self.v_right_target, 3)
            }
            try:
                json_data = json.dumps(packet) + "\n"
                self.serial_port.write(json_data.encode('utf-8'))
            except Exception as e:
                self.get_logger().error(f'Error writing to serial port: {e}')

    def update_loop(self):
        """
        20Hz Update Loop:
        1. Reads encoder telemetry from ESP32 (or simulates displacement in loopback mode).
        2. Integrates differential kinematics:
           d = (d_right + d_left) / 2
           d_theta = (d_right - d_left) / wheel_track
        3. Publishes /odom message and odom -> base_footprint transform.
        """
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        if dt <= 0.0:
            return

        # Calculate wheel displacements
        if self.is_hardware_connected and self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                data = json.loads(line)
                # ESP32 outputs delta wheel displacements or total tick counts
                d_left = data.get('d_l', self.v_left_target * dt)
                d_right = data.get('d_r', self.v_right_target * dt)
            except Exception:
                d_left = self.v_left_target * dt
                d_right = self.v_right_target * dt
        else:
            # Software Loopback simulation displacement
            d_left = self.v_left_target * dt
            d_right = self.v_right_target * dt

        # Differential Drive Kinematic Integration
        d_center = (d_right + d_left) / 2.0
        d_theta = (d_right - d_left) / self.wheel_track

        # Update pose estimation (x, y, theta)
        self.x += d_center * math.cos(self.theta + d_theta / 2.0)
        self.y += d_center * math.sin(self.theta + d_theta / 2.0)
        self.theta += d_theta

        # Normalize theta between -pi and pi
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        # Calculate velocities
        v_linear = d_center / dt
        v_angular = d_theta / dt

        # Quaternion calculation for orientation
        qz = math.sin(self.theta / 2.0)
        qw = math.cos(self.theta / 2.0)

        # 1. Publish TF Transform: odom -> base_footprint
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

        # 2. Publish /odom Odometry Message
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'

        odom_msg.pose.pose.position.x = self.x
        odom_msg.pose.pose.position.y = self.y
        odom_msg.pose.pose.position.z = 0.0
        odom_msg.pose.pose.orientation.z = qz
        odom_msg.pose.pose.orientation.w = qw

        odom_msg.twist.twist.linear.x = v_linear
        odom_msg.twist.twist.angular.z = v_angular

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
