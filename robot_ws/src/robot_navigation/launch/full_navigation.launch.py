import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """
    ROS 2 Master Navigation & Simulation Launch File for LUMI Healthcare Robot:
    1. Starts Gazebo simulation world & spawns LUMI differential-drive robot.
    2. Runs slam_toolbox for online 2D SLAM mapping (if use_slam is true).
    3. Runs Nav2 autonomous goal navigation stack (if use_nav2 is true).
    4. Launches RViz2 displaying live map, laser scans, costmaps, and goal tools.
    """

    pkg_robot_navigation = get_package_share_directory('robot_navigation')
    
    # Locate simulation package
    try:
        pkg_robot_simulation = get_package_share_directory('robot_simulation')
        gazebo_sim_launch_path = os.path.join(pkg_robot_simulation, 'launch', 'gazebo_sim.launch.py')
    except Exception:
        # Fallback to source repo layout
        pkg_simulation_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        gazebo_sim_launch_path = os.path.join(pkg_simulation_dir, 'simulation', 'launch', 'gazebo_sim.launch.py')

    slam_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'slam.launch.py')
    nav2_launch_path = os.path.join(pkg_robot_navigation, 'launch', 'navigation.launch.py')

    # Declare Launch Arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    use_slam_arg = DeclareLaunchArgument(
        'use_slam',
        default_value='true',
        description='Run SLAM Toolbox online mapping if true'
    )

    use_nav2_arg = DeclareLaunchArgument(
        'use_nav2',
        default_value='true',
        description='Run Nav2 autonomous navigation stack if true'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz2 if true'
    )

    # 1. Gazebo Simulation
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_sim_launch_path),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'use_rviz': LaunchConfiguration('use_rviz')
        }.items()
    )

    # 2. SLAM Mapping
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch_path),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items(),
        condition=IfCondition(LaunchConfiguration('use_slam'))
    )

    # 3. Nav2 Goal Navigation
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch_path),
        launch_arguments={'use_sim_time': LaunchConfiguration('use_sim_time')}.items(),
        condition=IfCondition(LaunchConfiguration('use_nav2'))
    )

    return LaunchDescription([
        use_sim_time_arg,
        use_slam_arg,
        use_nav2_arg,
        use_rviz_arg,
        gazebo_sim,
        slam,
        nav2
    ])
