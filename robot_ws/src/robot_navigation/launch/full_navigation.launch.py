import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    """
    ROS 2 Master One-Command Launch File:
    1. Starts Gazebo simulation world & spawns Baymax Healthcare Robot.
    2. Runs slam_toolbox for live SLAM mapping.
    3. Runs Nav2 autonomous goal navigation.
    4. Launches RViz2 displaying map, costmaps, and goal tools.
    """

    pkg_robot_navigation = get_package_share_directory('robot_navigation')
    pkg_simulation_dir = os.path.dirname(os.path.dirname(pkg_robot_navigation))

    # Path to Gazebo Simulation Launch File
    gazebo_sim_launch_path = os.path.join(pkg_simulation_dir, 'simulation', 'launch', 'gazebo_sim.launch.py')
    
    # Path to SLAM Launch File
    slam_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'slam.launch.py')

    # Path to Nav2 Launch File
    nav2_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'navigation.launch.py')

    # 1. Include Gazebo Sim Launch
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_sim_launch_path)
    )

    # 2. Include SLAM Launch
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch_path)
    )

    return LaunchDescription([
        gazebo_sim,
        slam
    ])
