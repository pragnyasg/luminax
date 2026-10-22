#!/usr/bin/env python3
"""LUMINAX robot bringup -- everything needed to drive and localize odometry.

Starts:
  * description  (robot_state_publisher + joint_state_publisher)
  * lidar        (RPLiDAR -> /scan)
  * rf2o         (/scan -> /odom + odom->base_footprint TF)
  * base         (motor_driver_node: /cmd_vel -> GPIO)

Run this on the ROBOT (the Raspberry Pi 5). Then teleop/SLAM/Nav from
the laptop over the same ROS 2 network.

Usage:
  ros2 launch luminax_bringup robot.launch.py
  ros2 launch luminax_bringup robot.launch.py serial_port:=/dev/ttyUSB0
  ros2 launch luminax_bringup robot.launch.py use_hardware:=false   # bench test
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    desc_share = get_package_share_directory('luminax_description')
    base_share = get_package_share_directory('luminax_base')
    bringup_share = get_package_share_directory('luminax_bringup')

    serial_port = LaunchConfiguration('serial_port')
    use_hardware = LaunchConfiguration('use_hardware')
    use_sim_time = LaunchConfiguration('use_sim_time')

    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(desc_share, 'launch', 'description.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )
    lidar = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_share, 'launch', 'lidar.launch.py')),
        launch_arguments={'serial_port': serial_port}.items(),
    )
    rf2o = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_share, 'launch', 'rf2o.launch.py')),
    )
    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(base_share, 'launch', 'base.launch.py')),
        launch_arguments={'use_hardware': use_hardware}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('use_hardware', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        description,
        lidar,
        rf2o,
        base,
    ])
