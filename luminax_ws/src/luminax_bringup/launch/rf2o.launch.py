#!/usr/bin/env python3
"""Start rf2o_laser_odometry: laser-scan odometry + odom->base_footprint TF.

Requires the source package `rf2o_laser_odometry` to be built in this
workspace (see README). Expects /scan to already be publishing.

Usage:
  ros2 launch luminax_bringup rf2o.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('luminax_bringup')
    default_params = os.path.join(pkg_share, 'config', 'rf2o.yaml')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default_params,
                              description='rf2o params YAML.'),
        Node(
            package='rf2o_laser_odometry',
            executable='rf2o_laser_odometry_node',
            name='rf2o_laser_odometry',
            output='screen',
            parameters=[params_file],
        ),
    ])
