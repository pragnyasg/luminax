#!/usr/bin/env python3
"""Launch the LUMINAX motor driver node.

Usage:
  ros2 launch luminax_base base.launch.py
  ros2 launch luminax_base base.launch.py use_hardware:=false   # laptop test
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('luminax_base')
    default_params = os.path.join(pkg_share, 'config', 'base_params.yaml')

    params_file = LaunchConfiguration('params_file')
    use_hardware = LaunchConfiguration('use_hardware')

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default_params,
                              description='Motor driver params YAML.'),
        DeclareLaunchArgument('use_hardware', default_value='true',
                              description='false = dry-run (no GPIO).'),
        Node(
            package='luminax_base',
            executable='motor_driver_node',
            name='motor_driver_node',
            output='screen',
            parameters=[params_file, {'use_hardware': use_hardware}],
        ),
    ])
