#!/usr/bin/env python3
"""Start the RPLiDAR A1 driver and publish /scan in frame 'laser_frame'.

Requires the Slamtec driver `sllidar_ros2` to be built in this workspace
(see README -> "Third-party source packages"). RPLiDAR A1 uses baud 115200.

Usage:
  ros2 launch luminax_bringup lidar.launch.py
  ros2 launch luminax_bringup lidar.launch.py serial_port:=/dev/ttyUSB0
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port')
    frame_id = LaunchConfiguration('frame_id')

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0',
                              description='LiDAR serial device.'),
        DeclareLaunchArgument('frame_id', default_value='laser_frame',
                              description='TF frame the scan is published in '
                                          '(must match the URDF laser link).'),
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            output='screen',
            parameters=[{
                'serial_port': serial_port,
                'serial_baudrate': 115200,     # A1 = 115200 ; A2/A3 differ
                'frame_id': frame_id,
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Standard',
            }],
        ),
    ])
