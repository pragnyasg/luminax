import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    """
    Master Full System Bringup Launch File for Baymax Healthcare Robot.
    
    Starts the complete integrated robot stack:
    1. Gazebo Classic 11 Simulation World & Spawns Robot Entity.
    2. SLAM Mapping (slam_toolbox) & Nav2 Goal Navigation Stack.
    3. Person Detection Perception Node (OpenCV).
    4. Voice Synthesis & Interaction Node.
    5. Healthcare Reminder Manager Node.
    6. Companion Behavior Manager Finite State Machine (FSM) Node.
    """

    pkg_robot_navigation = get_package_share_directory('robot_navigation')

    # Path to Full Navigation Launch File (Gazebo + SLAM + Nav2 + RViz)
    full_nav_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'full_navigation.launch.py')

    # 1. Include Full Navigation Launch
    navigation_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(full_nav_launch_path)
    )

    # 2. Perception: Person Detector Node
    person_detector_node = Node(
        package='robot_perception',
        executable='person_detector_node',
        name='person_detector_node',
        output='screen'
    )

    # 3. Voice Interaction Node
    voice_node = Node(
        package='robot_voice',
        executable='voice_node',
        name='voice_node',
        output='screen'
    )

    # 4. Healthcare Reminder Manager Node
    reminder_manager_node = Node(
        package='robot_health',
        executable='reminder_manager_node',
        name='reminder_manager_node',
        output='screen'
    )

    # 5. Behavior Manager FSM Node
    behaviour_manager_node = Node(
        package='robot_behaviour',
        executable='behaviour_manager_node',
        name='behaviour_manager_node',
        output='screen'
    )

    return LaunchDescription([
        navigation_stack,
        person_detector_node,
        voice_node,
        reminder_manager_node,
        behaviour_manager_node
    ])
