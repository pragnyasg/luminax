#!/usr/bin/env python3
"""Publish the LUMINAX robot description and TF tree.

Runs:
  * robot_state_publisher  -> publishes all fixed TFs + /robot_description
  * joint_state_publisher  -> publishes zero positions for the wheel joints
                              so robot_state_publisher can complete the tree
                              (we have no encoders; wheels will not visually
                              spin, but their frames will exist for RViz).
  * rviz2 (optional)       -> set rviz:=true to open a preconfigured view.

Usage:
  ros2 launch luminax_description description.launch.py
  ros2 launch luminax_description description.launch.py rviz:=true
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('luminax_description')
    default_xacro = os.path.join(pkg_share, 'urdf', 'luminax.urdf.xacro')
    default_rviz = os.path.join(pkg_share, 'rviz', 'luminax.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')

    # Expand the xacro at launch time into the robot_description parameter.
    robot_description = {
        'robot_description': Command([
            'xacro ', default_xacro
        ]),
        'use_sim_time': use_sim_time,
    }

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use /clock if true (simulation).'),
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='Open RViz2 with the LUMINAX config.'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[robot_description],
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            condition=IfCondition(rviz),
            arguments=['-d', default_rviz],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])
