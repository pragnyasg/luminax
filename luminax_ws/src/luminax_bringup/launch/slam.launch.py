#!/usr/bin/env python3
"""Build a map with slam_toolbox (online async).

By default this also brings up the robot (lidar + rf2o + base + description).
Drive with teleop_twist_keyboard, then save the map (see README, Step 6).

Usage:
  ros2 launch luminax_bringup slam.launch.py
  ros2 launch luminax_bringup slam.launch.py use_robot:=false  # robot already up
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_share = get_package_share_directory('luminax_bringup')
    slam_params = os.path.join(bringup_share, 'config',
                               'mapper_params_online_async.yaml')

    use_robot = LaunchConfiguration('use_robot')
    use_sim_time = LaunchConfiguration('use_sim_time')
    serial_port = LaunchConfiguration('serial_port')

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_share, 'launch', 'robot.launch.py')),
        launch_arguments={'serial_port': serial_port,
                          'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(use_robot),
    )

    slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params, {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_robot', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        robot,
        slam,
    ])
