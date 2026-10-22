#!/usr/bin/env python3
"""Autonomous navigation with Nav2 on a previously saved map.

By default also brings up the robot (lidar + rf2o + base + description)
and starts AMCL localization against the saved map.

Usage:
  ros2 launch luminax_bringup navigation.launch.py map:=$HOME/luminax_ws/maps/home.yaml
  ros2 launch luminax_bringup navigation.launch.py map:=.../home.yaml use_robot:=false

Then in RViz2 (on the laptop) use "2D Pose Estimate" to seed AMCL and
"2D Goal Pose" to send navigation goals.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_share = get_package_share_directory('luminax_bringup')
    nav2_bringup_share = get_package_share_directory('nav2_bringup')
    nav2_params = os.path.join(bringup_share, 'config', 'nav2_params.yaml')

    map_yaml = LaunchConfiguration('map')
    use_robot = LaunchConfiguration('use_robot')
    use_sim_time = LaunchConfiguration('use_sim_time')
    serial_port = LaunchConfiguration('serial_port')
    params_file = LaunchConfiguration('params_file')

    robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_share, 'launch', 'robot.launch.py')),
        launch_arguments={'serial_port': serial_port,
                          'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(use_robot),
    )

    # Reuse the official nav2_bringup bringup_launch.py (localization + nav).
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_share, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': 'true',
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value='',
                              description='Path to the saved map .yaml.'),
        DeclareLaunchArgument('params_file', default_value=nav2_params),
        DeclareLaunchArgument('use_robot', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        robot,
        nav2,
    ])
