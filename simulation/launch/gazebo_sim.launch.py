import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    """
    ROS 2 Humble Master Gazebo Simulation Launch File.
    
    1. Launches Gazebo Classic 11 server & client.
    2. Runs robot_state_publisher for Xacro description.
    3. Spawns Baymax Healthcare Robot into Gazebo room world.
    4. Opens RViz2 displaying simulated LiDAR scans and camera feeds.
    """

    # Package Directory Paths
    pkg_robot_description = get_package_share_directory('robot_description')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    
    # File Paths
    xacro_file_path = os.path.join(pkg_robot_description, 'urdf', 'healthcare_robot.urdf.xacro')
    rviz_config_path = os.path.join(pkg_robot_description, 'rviz', 'robot.rviz')
    world_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'worlds', 'healthcare_room.world')

    # Process Xacro
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file_path]),
        value_type=str
    )

    # 1. Gazebo Server (gzserver)
    start_gazebo_server_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file_path}.items()
    )

    # 2. Gazebo Client (gzclient)
    start_gazebo_client_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # 3. Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    # 4. Spawn Robot Entity Node in Gazebo
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=[
            '-entity', 'healthcare_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ]
    )

    # 5. RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    return LaunchDescription([
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        robot_state_publisher_node,
        spawn_robot_node,
        rviz_node
    ])
